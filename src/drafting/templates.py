"""
Fallback LinkedIn post templates for People on the Move.
Used when Claude API is unavailable.
"""
import random
from typing import Dict, List

# Template variations for different actions
TEMPLATES = {
    'appointed': [
        """{person_name} has been appointed {new_title} at {company_name}.

{hashtags}""",

        """{company_name} has named {person_name} as {new_title}.

{hashtags}""",
    ],

    'promoted': [
        """{person_name} has been promoted to {new_title} at {company_name}.

{hashtags}""",

        """{company_name} has promoted {person_name} to {new_title}.

{hashtags}""",
    ],

    'joins': [
        """{person_name} has joined {company_name} as {new_title}.

{hashtags}""",

        """{person_name} joins {company_name} as {new_title}.

{hashtags}""",
    ],

    'default': [
        """{person_name} is now {new_title} at {company_name}.

{hashtags}""",

        """{company_name} announces {person_name} as {new_title}.

{hashtags}""",
    ],
}

# Default hashtags
DEFAULT_HASHTAGS = [
    "#MeatIndustry",
    "#PoultryIndustry",
    "#PeopleOnTheMove",
    "#Leadership",
    "#FoodIndustry",
    "#CareerMoves",
    "#Congratulations",
]


def format_hashtags(company_name: str = None, count: int = 5) -> str:
    """Generate hashtag string."""
    hashtags = DEFAULT_HASHTAGS[:count]

    # Add company-specific hashtag if possible
    if company_name:
        # Create hashtag from company name (remove spaces, special chars)
        company_tag = "#" + "".join(
            word.capitalize() for word in company_name.split()
            if word.isalnum()
        )
        if len(company_tag) > 2:
            hashtags.insert(0, company_tag)
            hashtags = hashtags[:count]

    return " ".join(hashtags)


def select_template(action: str = None) -> str:
    """Select a random template based on action type."""
    # Normalize action
    if action:
        action = action.lower()
        if 'promot' in action:
            action = 'promoted'
        elif 'appoint' in action or 'named' in action:
            action = 'appointed'
        elif 'join' in action or 'hire' in action:
            action = 'joins'
        else:
            action = 'default'
    else:
        action = 'default'

    templates = TEMPLATES.get(action, TEMPLATES['default'])
    return random.choice(templates)


def generate_post_from_template(announcement: Dict) -> str:
    """
    Generate a LinkedIn post from an announcement using templates.

    Args:
        announcement: Dict with keys:
            - person_name: Name of the executive
            - new_title: New position
            - company_name: Company name
            - action: Type of move (optional)
            - previous_title: Previous position (optional)
            - previous_company: Previous company (optional)

    Returns:
        Formatted LinkedIn post string
    """
    # Get values with defaults
    person_name = announcement.get('person_name', 'this executive')
    new_title = announcement.get('new_title', 'their new role')
    company_name = announcement.get('company_name', 'the company')
    action = announcement.get('action', 'default')

    # Generate hashtags
    hashtags = format_hashtags(company_name)

    # Select and fill template
    template = select_template(action)

    post = template.format(
        person_name=person_name,
        new_title=new_title,
        company_name=company_name,
        hashtags=hashtags,
    )

    return post.strip()


def generate_minimal_post(person_name: str, new_title: str, company_name: str) -> str:
    """Generate a minimal post with just the essential information."""
    hashtags = format_hashtags(company_name, count=3)

    return f"""{person_name} is now {new_title} at {company_name}.

{hashtags}"""
