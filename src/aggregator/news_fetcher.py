"""
News fetcher for People on the Move.
Fetches news from RSS feeds and News APIs, then parses for executive moves.
"""
import time
import logging
from typing import List, Dict, Optional, Generator
from datetime import datetime, timedelta

import feedparser
import requests

from config import settings
from .rss_sources import (
    get_all_rss_feeds,
    build_google_news_url,
    get_company_newsroom_feed,
    get_prnewswire_company_url,
    EXECUTIVE_MOVE_QUERIES
)

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    logger.warning("BeautifulSoup not installed. PR Newswire scraping disabled. Run: pip install beautifulsoup4")
from .parsers import ArticleParser, find_company_in_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetch news from various sources."""

    def __init__(self):
        self.parser = ArticleParser()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; PeopleOnTheMove/1.0)'
        })

    def fetch_rss_feed(self, feed_url: str, max_items: int = 50) -> List[Dict]:
        """
        Fetch and parse an RSS feed.

        Returns list of article dicts with:
        - title, content, link, published, source_name
        """
        try:
            feed = feedparser.parse(feed_url)

            if feed.bozo and not feed.entries:
                logger.warning(f"Failed to parse RSS feed: {feed_url}")
                return []

            articles = []
            for entry in feed.entries[:max_items]:
                article = {
                    'title': entry.get('title', ''),
                    'content': entry.get('summary', entry.get('description', '')),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', entry.get('updated', '')),
                    'source_name': feed.feed.get('title', 'RSS Feed'),
                }
                articles.append(article)

            logger.info(f"Fetched {len(articles)} articles from {feed_url}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
            return []

    def fetch_google_news(self, company_name: str, days_back: int = 7) -> List[Dict]:
        """
        Fetch news about a company from Google News RSS.

        Args:
            company_name: Name of company to search for
            days_back: How many days of news to fetch

        Returns:
            List of article dicts
        """
        all_articles = []

        for query_template in EXECUTIVE_MOVE_QUERIES[:6]:  # Use more queries for better coverage
            url = build_google_news_url(company_name, query_template)
            articles = self.fetch_rss_feed(url, max_items=20)
            all_articles.extend(articles)

            # Be nice to Google
            time.sleep(0.5)

        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['link'] not in seen_urls:
                seen_urls.add(article['link'])
                unique_articles.append(article)

        return unique_articles

    def fetch_newsapi(self, company_name: str, days_back: int = 7) -> List[Dict]:
        """
        Fetch news from NewsAPI.org.

        Requires NEWSAPI_KEY in settings.
        """
        if not settings.NEWSAPI_KEY:
            logger.debug("NewsAPI key not configured, skipping")
            return []

        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

            url = "https://newsapi.org/v2/everything"
            params = {
                'q': f'"{company_name}" AND (appointed OR promoted OR named OR hires OR VP OR director OR executive)',
                'from': from_date,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 100,
                'apiKey': settings.NEWSAPI_KEY
            }

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            articles = []
            for item in data.get('articles', []):
                articles.append({
                    'title': item.get('title', ''),
                    'content': item.get('description', '') or item.get('content', ''),
                    'link': item.get('url', ''),
                    'published': item.get('publishedAt', ''),
                    'source_name': item.get('source', {}).get('name', 'NewsAPI'),
                })

            logger.info(f"Fetched {len(articles)} articles from NewsAPI for {company_name}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching from NewsAPI for {company_name}: {e}")
            return []

    def fetch_company_newsroom(self, company_name: str) -> List[Dict]:
        """Fetch from company-specific newsroom RSS feed."""
        feed_url = get_company_newsroom_feed(company_name)
        if not feed_url:
            return []

        articles = self.fetch_rss_feed(feed_url)
        # Mark source as company newsroom
        for article in articles:
            article['source_name'] = f"{company_name} Newsroom"

        return articles

    def fetch_prnewswire_company(self, company_name: str, max_items: int = 25) -> List[Dict]:
        """
        Scrape PR Newswire company page for press releases.

        PR Newswire doesn't offer company-specific RSS feeds, so we scrape
        the HTML pages to extract press release listings.

        Args:
            company_name: Name of company to fetch
            max_items: Maximum number of releases to fetch

        Returns:
            List of article dicts
        """
        if not HAS_BS4:
            logger.debug("BeautifulSoup not available, skipping PR Newswire scraping")
            return []

        page_url = get_prnewswire_company_url(company_name)
        if not page_url:
            logger.debug(f"No PR Newswire page configured for {company_name}")
            return []

        try:
            response = self.session.get(page_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []

            # Find news release cards - PR Newswire uses various card layouts
            # Look for common patterns: article cards, news items, release links
            news_items = soup.find_all('a', class_=lambda x: x and ('newsreleaseconsolidatelink' in x.lower() or 'card' in x.lower()))

            # Also try finding by href pattern for news releases
            if not news_items:
                news_items = soup.find_all('a', href=lambda x: x and '/news-releases/' in x)

            seen_urls = set()
            for item in news_items:
                if len(articles) >= max_items:
                    break

                href = item.get('href', '')
                if not href or '/news-releases/' not in href:
                    continue

                # Build full URL
                if href.startswith('/'):
                    full_url = f"https://www.prnewswire.com{href}"
                else:
                    full_url = href

                # Skip duplicates
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)

                # Extract title from link text or nearby heading
                # Use separator to avoid word concatenation
                title = item.get_text(separator=' ', strip=True)

                if not title or len(title) < 10:
                    # Try to find title in parent or nearby elements
                    parent = item.find_parent(['article', 'div', 'li'])
                    if parent:
                        h_tag = parent.find(['h1', 'h2', 'h3', 'h4'])
                        if h_tag:
                            title = h_tag.get_text(separator=' ', strip=True)

                if not title or len(title) < 10:
                    continue

                # Try to extract date from nearby elements or from title prefix
                published = ''
                parent = item.find_parent(['article', 'div', 'li'])

                # PR Newswire often has date embedded at start of title: "Feb 24, 2026, 16:30 ETActual Title..."
                import re
                date_pattern = r'^((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}(?:,\s+\d{1,2}:\d{2}\s*(?:ET|PT|CT|MT))?)\s*'
                date_match = re.match(date_pattern, title, re.IGNORECASE)
                if date_match:
                    published = date_match.group(1).strip()
                    # Remove date prefix from title
                    title = title[date_match.end():].strip()

                if not published and parent:
                    # Look for time/date elements
                    time_el = parent.find(['time', 'span'], class_=lambda x: x and ('date' in x.lower() or 'time' in x.lower()))
                    if time_el:
                        published = time_el.get('datetime', '') or time_el.get_text(strip=True)
                    else:
                        # Look for date patterns in text
                        for span in parent.find_all('span'):
                            text = span.get_text(strip=True)
                            # Simple date pattern check (e.g., "Feb 24, 2026")
                            if any(month in text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                                published = text
                                break

                # Extract summary/description if available
                content = ''
                if parent:
                    p_tag = parent.find('p')
                    if p_tag:
                        content = p_tag.get_text(strip=True)

                articles.append({
                    'title': title,
                    'content': content or title,  # Use title as fallback content
                    'link': full_url,
                    'published': published,
                    'source_name': f'PR Newswire - {company_name}',
                })

            logger.info(f"Scraped {len(articles)} releases from PR Newswire for {company_name}")
            return articles

        except Exception as e:
            logger.error(f"Error scraping PR Newswire for {company_name}: {e}")
            return []

    def fetch_industry_feeds(self) -> List[Dict]:
        """Fetch all industry RSS feeds."""
        all_articles = []

        for feed in get_all_rss_feeds():
            articles = self.fetch_rss_feed(
                feed['url'],
                max_items=settings.MAX_ARTICLES_PER_SOURCE
            )
            # Add source name from config
            for article in articles:
                article['source_name'] = feed['name']
            all_articles.extend(articles)

            # Be respectful to servers
            time.sleep(0.3)

        return all_articles


class NewsAggregator:
    """
    Main aggregator that fetches news and extracts executive move data.
    """

    def __init__(self, companies: List[Dict]):
        """
        Initialize aggregator.

        Args:
            companies: List of company dicts with 'id', 'name', 'aliases'
        """
        self.companies = companies
        self.fetcher = NewsFetcher()
        self.parser = ArticleParser()

    def process_articles(self, articles: List[Dict],
                         target_company: Dict = None,
                         max_age_days: int = None) -> Generator[Dict, None, None]:
        """
        Process articles and yield structured announcement data.

        Args:
            articles: List of raw article dicts
            target_company: If provided, only match this company
            max_age_days: If provided, filter out articles older than this

        Yields:
            Dict with announcement data ready for database
        """
        for article in articles:
            # Parse article for executive move
            parsed = self.parser.parse_article(
                title=article.get('title', ''),
                content=article.get('content', ''),
                published_date=article.get('published'),
                source_url=article.get('link'),
                source_name=article.get('source_name'),
                max_age_days=max_age_days
            )

            if not parsed:
                continue

            # Find company mentioned in article
            combined_text = f"{article.get('title', '')} {article.get('content', '')}"

            if target_company:
                # Verify target company is mentioned
                if not find_company_in_text(combined_text, [target_company]):
                    continue
                company = target_company
            else:
                # Search for any tracked company
                company = find_company_in_text(combined_text, self.companies)
                if not company:
                    continue

            # Add company info to parsed data
            parsed['company_id'] = company.get('id')
            parsed['company_name'] = company.get('name')

            yield parsed

    def fetch_for_company(self, company: Dict, days_back: int = 7) -> List[Dict]:
        """
        Fetch all news for a specific company.

        Args:
            company: Company dict with 'id', 'name', 'aliases'
            days_back: How many days of news to fetch

        Returns:
            List of structured announcement dicts
        """
        logger.info(f"Fetching news for {company['name']}...")

        all_articles = []

        # Fetch from Google News
        google_articles = self.fetcher.fetch_google_news(
            company['name'],
            days_back=days_back
        )
        all_articles.extend(google_articles)

        # Fetch from NewsAPI if configured
        newsapi_articles = self.fetcher.fetch_newsapi(
            company['name'],
            days_back=days_back
        )
        all_articles.extend(newsapi_articles)

        # Fetch from company newsroom
        newsroom_articles = self.fetcher.fetch_company_newsroom(company['name'])
        all_articles.extend(newsroom_articles)

        # Fetch from PR Newswire company page (scraped)
        prnewswire_articles = self.fetcher.fetch_prnewswire_company(company['name'])
        all_articles.extend(prnewswire_articles)

        # Process all articles (filter by date handled in run script)
        announcements = list(self.process_articles(
            all_articles,
            target_company=company
        ))

        logger.info(f"Found {len(announcements)} executive moves for {company['name']}")
        return announcements

    def fetch_all(self, days_back: int = 7) -> List[Dict]:
        """
        Fetch news for all companies.

        Args:
            days_back: How many days of news to fetch

        Returns:
            List of all structured announcement dicts
        """
        all_announcements = []

        # First, fetch industry feeds (applies to all companies)
        logger.info("Fetching industry feeds...")
        industry_articles = self.fetcher.fetch_industry_feeds()
        industry_announcements = list(self.process_articles(industry_articles))
        all_announcements.extend(industry_announcements)

        # Then fetch company-specific news
        for company in self.companies:
            company_announcements = self.fetch_for_company(company, days_back)
            all_announcements.extend(company_announcements)

            # Be respectful to APIs
            time.sleep(1)

        # Deduplicate by source_url
        seen_urls = set()
        unique = []
        for ann in all_announcements:
            url = ann.get('source_url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(ann)
            elif not url:
                # Keep items without URL but may have duplicates
                unique.append(ann)

        logger.info(f"Total unique announcements found: {len(unique)}")
        return unique
