"""
Parsers for extracting structured data from news articles.
"""
import re
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
from dateutil import parser as date_parser
from bs4 import BeautifulSoup

from .rss_sources import EXECUTIVE_TITLES, EXECUTIVE_KEYWORDS

# Blacklist of known false positives for person names
# These are publication names, company names, and common phrases that get incorrectly extracted
FALSE_POSITIVE_NAMES: Set[str] = {
    # News publications
    'supermarket news', 'progressive grocer', 'grocery dive', 'food dive',
    'meat poultry', 'meat + poultry', 'reuters', 'associated press', 'ap news',
    'business wire', 'pr newswire', 'globe newswire', 'cision', 'yahoo finance',
    'wall street journal', 'new york times', 'bloomberg', 'cnbc', 'fox business',
    'food business news', 'food navigator', 'the packer', 'produce news',
    'watt poultry', 'national provisioner', 'perishable news', 'spectrum news',
    'xavier newswire', 'investment executive', 'industry dive',

    # Common false positive phrases
    'quietly setting up', 'business chief', 'warns of', 'brings walmart experience',
    'walmart executive', 'settled this lawsuit', 'grocery chain', 'retail giant',
    'food company', 'meat company', 'industry veteran', 'company announces',
    'press release', 'news release', 'breaking news', 'just announced',
    'read more', 'click here', 'learn more', 'see more', 'view all',
    'president trump', 'president biden', 'president obama',
    'greg foran takes', 'brings experience', 'takes helm', 'steps down',
    'steps up', 'moves up', 'moves on', 'stepping down', 'stepping up',

    # Company name fragments that appear as names
    'butterball farms', 'tyson foods', 'hormel foods', 'cargill inc',
    'jbs usa', 'smithfield foods', 'pilgrim pride', 'perdue farms',
    'conagra brands', 'kraft heinz', 'general mills', 'kellogg company',
    'nestle usa', 'unilever usa', 'pepsico inc', 'coca cola',

    # Generic terms
    'new ceo', 'new president', 'new cfo', 'new coo', 'next ceo',
    'its next ceo', 'new hire', 'top executive', 'senior executive',
    'board member', 'board director', 'company executive',
}

# Words that should never start a person's name
INVALID_FIRST_WORDS: Set[str] = {
    'the', 'a', 'an', 'new', 'former', 'current', 'acting', 'interim',
    'its', 'their', 'our', 'your', 'his', 'her', 'this', 'that',
    'brings', 'quietly', 'business', 'walmart', 'kroger', 'tyson',
    'supermarket', 'progressive', 'grocery', 'food', 'meat', 'industry',
    'company', 'corporate', 'executive', 'president', 'investment',
    'retail', 'wholesale', 'breaking', 'just', 'press', 'news',
    'warns', 'settled', 'takes', 'steps', 'moves', 'stepping',
    'read', 'click', 'learn', 'see', 'view', 'get', 'how', 'why',
    'what', 'when', 'where', 'who', 'which', 'here', 'there',
    # Job titles/descriptors that precede names
    'vet', 'veteran', 'longtime', 'seasoned', 'senior', 'junior',
    'chief', 'ceo', 'cfo', 'coo', 'cto', 'cmo', 'vp', 'svp', 'evp',
    'director', 'manager', 'head', 'leader', 'founder', 'owner',
}

# Words that should never end a person's name
INVALID_LAST_WORDS: Set[str] = {
    'news', 'grocer', 'dive', 'wire', 'times', 'journal', 'post',
    'tribune', 'herald', 'gazette', 'press', 'media', 'report',
    'foods', 'farms', 'inc', 'corp', 'corporation', 'company', 'co',
    'llc', 'ltd', 'group', 'holdings', 'brands', 'products',
    'experience', 'chief', 'executive', 'lawsuit', 'helm',
    'ceo', 'cfo', 'coo', 'cto', 'cmo', 'vp', 'svp', 'evp',
    'up', 'down', 'on', 'off', 'out', 'in', 'here', 'there',
}


class ArticleParser:
    """Parse article content to extract executive move information."""

    def __init__(self):
        # Build regex patterns for title matching
        self.title_patterns = self._build_title_patterns()
        self.action_patterns = self._build_action_patterns()

    def _build_title_patterns(self) -> List[re.Pattern]:
        """Build regex patterns for job titles."""
        patterns = []
        for title in EXECUTIVE_TITLES:
            # Create case-insensitive pattern
            pattern = re.compile(
                rf'\b{re.escape(title)}\b',
                re.IGNORECASE
            )
            patterns.append(pattern)
        return patterns

    def _build_action_patterns(self) -> List[Tuple[re.Pattern, str]]:
        """Build regex patterns for action words with their meanings."""
        actions = [
            (r'\bappointed\s+(?:as\s+)?(.+?)(?:\.|,|$)', 'appointed'),
            (r'\bnamed\s+(?:as\s+)?(.+?)(?:\.|,|$)', 'named'),
            (r'\bpromoted\s+to\s+(.+?)(?:\.|,|$)', 'promoted'),
            (r'\bjoins\s+(?:as\s+)?(.+?)(?:\.|,|$)', 'joins'),
            (r'\bhires\s+(.+?)\s+as\s+(.+?)(?:\.|,|$)', 'hires'),
            (r'\bnamed\s+(.+?)\s+as\s+new\s+(.+?)(?:\.|,|$)', 'new'),
        ]
        return [(re.compile(p, re.IGNORECASE), a) for p, a in actions]

    def is_executive_move(self, title: str, content: str = "") -> bool:
        """Check if article is about an executive move."""
        combined_text = f"{title} {content}".lower()

        # Check for executive keywords
        keyword_match = any(kw in combined_text for kw in EXECUTIVE_KEYWORDS)
        if not keyword_match:
            return False

        # Check for job titles
        title_match = any(p.search(combined_text) for p in self.title_patterns)
        return title_match

    def extract_person_name(self, text: str) -> Optional[str]:
        """Extract person name from text."""
        # Common patterns for names in announcements
        # Note: Order matters - more specific patterns should come first
        patterns = [
            # "Appoints/Names John Smith as..." (PR Newswire headline style)
            r'(?:Appoints|Names|Taps|Hires|Promotes|Selects|Elevates)\s+([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:as|to|for|Group)',
            # "Appointment of John Smith..." (PR Newswire style)
            r'Appointment\s+of\s+([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            # "John Smith has been appointed..."
            r'^([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:has been|was|is|will)',
            # "...appointed John Smith as..." (lowercase)
            r'(?:appointed|named|hired|promotes?|taps|selects|elevates)\s+([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:as|to|for)',
            # "...welcomes John Smith..."
            r'(?:welcomes?|announces?)\s+([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            # "John Smith joins..."
            r'([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:joins|named|appointed|to lead|to head|becomes)',
            # "John Smith, CEO..."
            r'([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),?\s+(?:the new|new|as|named)',
            # "CEO John Smith..."
            r'(?:CEO|President|CFO|COO|VP|Director)\s+([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            # "...names John Smith CEO..."
            r'names\s+([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:CEO|President|CFO|COO|VP|Director|Chief)',
            # "...John Smith to CEO..."
            r'([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+to\s+(?:CEO|President|CFO|COO|VP|Director|Chief)',
            # "...hires John Smith..."
            r'hires\s+([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            # "John Smith promoted..."
            r'([A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:promoted|elevated|tapped)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                # Validate the extracted name
                if self._is_valid_person_name(name):
                    return name

        return None

    def _is_valid_person_name(self, name: str) -> bool:
        """
        Validate that an extracted string is likely a real person's name.

        Returns True if the name passes all validation checks.
        """
        if not name:
            return False

        # Check against full name blacklist (case-insensitive)
        name_lower = name.lower()
        if name_lower in FALSE_POSITIVE_NAMES:
            return False

        # Check word count (should be 2-4 words for a person's name)
        words = name.split()
        if not (2 <= len(words) <= 4):
            return False

        # Check first word against invalid first words
        first_word = words[0].lower()
        if first_word in INVALID_FIRST_WORDS:
            return False

        # Check last word against invalid last words
        last_word = words[-1].lower()
        if last_word in INVALID_LAST_WORDS:
            return False

        # Check that first word looks like a first name (starts with capital, rest lowercase)
        # and is not all caps (like "CEO" or "CFO")
        if words[0].isupper() and len(words[0]) > 1:
            return False

        # Check for common publication/company patterns
        # "X News", "X Dive", "X Wire", etc.
        if len(words) >= 2:
            second_word_lower = words[1].lower()
            if second_word_lower in {'news', 'dive', 'wire', 'grocer', 'times', 'journal',
                                      'post', 'tribune', 'herald', 'gazette', 'foods',
                                      'farms', 'brands', 'executive'}:
                return False

        # Check that the name doesn't contain suspicious patterns
        # e.g., "Liate Stehlik Promoted" - check if last word is a verb
        verbs_as_names = {'promoted', 'appointed', 'named', 'hired', 'takes',
                          'joins', 'becomes', 'steps', 'moves', 'brings'}
        if words[-1].lower() in verbs_as_names:
            return False

        # Check for "President X" pattern where X is a political figure
        if len(words) >= 2 and words[0].lower() == 'president':
            # Allow "President" as a title only if followed by a regular name
            # but filter out "President Trump", "President Biden", etc.
            political_names = {'trump', 'biden', 'obama', 'bush', 'clinton'}
            if words[1].lower() in political_names:
                return False

        # Additional check: name should not contain common non-name words in middle
        middle_words = words[1:-1] if len(words) > 2 else []
        non_name_middle_words = {'and', 'or', 'the', 'of', 'for', 'at', 'in', 'on',
                                  'to', 'as', 'its', 'their', 'new', 'next'}
        for word in middle_words:
            if word.lower() in non_name_middle_words and len(word) <= 3:
                return False

        return True

    def extract_title(self, text: str) -> Optional[str]:
        """Extract job title from text."""
        for pattern in self.title_patterns:
            match = pattern.search(text)
            if match:
                # Get surrounding context
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]

                # Try to get full title with modifiers
                full_title_match = re.search(
                    rf'(?:as|to|new)\s+((?:\w+\s+)*{re.escape(match.group())}(?:\s+of\s+\w+)?)',
                    context,
                    re.IGNORECASE
                )
                if full_title_match:
                    return full_title_match.group(1).strip()

                return match.group()

        return None

    def extract_action(self, text: str) -> Optional[str]:
        """Determine the type of executive move (appointed, promoted, etc.)."""
        text_lower = text.lower()

        if 'promoted' in text_lower:
            return 'promoted to'
        elif 'appoints' in text_lower or 'appointed' in text_lower:
            return 'appointed'
        elif 'taps' in text_lower or 'tapped' in text_lower:
            return 'tapped as'
        elif 'names' in text_lower or 'named' in text_lower:
            return 'named'
        elif 'joins' in text_lower or 'hired' in text_lower or 'hires' in text_lower:
            return 'joins as'
        elif 'announces' in text_lower or 'appointment' in text_lower:
            return 'announced as'

        return 'named'

    def clean_html(self, html_content: str) -> str:
        """Remove HTML tags and clean up text."""
        soup = BeautifulSoup(html_content, 'lxml')
        text = soup.get_text(separator=' ')
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats."""
        if not date_str:
            return None
        try:
            return date_parser.parse(date_str)
        except (ValueError, TypeError):
            return None

    def parse_article(self, title: str, content: str, published_date: str = None,
                      source_url: str = None, source_name: str = None,
                      max_age_days: int = None) -> Optional[Dict]:
        """
        Parse an article and extract structured executive move data.

        Returns dict with:
        - person_name: Name of the executive
        - new_title: New position/title
        - action: Type of move (appointed, promoted, etc.)
        - raw_text: Cleaned article text
        - source_url: Link to article
        - source_name: Publication name
        - announcement_date: Date of announcement (from RSS feed published date only)
        """
        # Clean content
        clean_content = self.clean_html(content) if content else ""
        combined_text = f"{title} {clean_content}"

        # Check if this is an executive move article
        if not self.is_executive_move(title, clean_content):
            return None

        # Parse the RSS published date (not dates from content)
        announcement_date = self.parse_date(published_date)

        # Filter by age if max_age_days specified
        if max_age_days and announcement_date:
            from datetime import timedelta
            cutoff = datetime.now() - timedelta(days=max_age_days)
            # Handle timezone-aware datetimes
            ann_date = announcement_date.replace(tzinfo=None) if announcement_date.tzinfo else announcement_date
            if ann_date < cutoff:
                return None

        # Extract information
        person_name = self.extract_person_name(combined_text)
        new_title = self.extract_title(combined_text)
        action = self.extract_action(combined_text)

        # Must have a valid person name to be useful
        # (title alone is not enough - we need to know WHO was appointed)
        if not person_name:
            return None

        return {
            'person_name': person_name,
            'new_title': new_title,
            'action': action,
            'raw_text': combined_text[:2000],  # Limit stored text
            'source_url': source_url,
            'source_name': source_name,
            'announcement_date': announcement_date.date() if announcement_date else None,
        }


def find_company_in_text(text: str, companies: List[Dict]) -> Optional[Dict]:
    """
    Find which company is mentioned in the text.

    Args:
        text: Article text to search
        companies: List of company dicts with 'name' and optional 'aliases'

    Returns:
        Company dict if found, None otherwise
    """
    text_lower = text.lower()

    for company in companies:
        # Check main company name
        if company['name'].lower() in text_lower:
            return company

        # Check aliases
        for alias in company.get('aliases', []):
            if alias.lower() in text_lower:
                return company

    return None
