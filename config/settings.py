"""
Configuration settings for People on the Move application.
Loads environment variables from .env file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = PROJECT_ROOT / "config"

# Database - supports both SQLite (local) and PostgreSQL (production)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Default to SQLite for local development
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/potm.db")
    DATABASE_URL = f"sqlite:///{PROJECT_ROOT / DATABASE_PATH}"
elif DATABASE_URL.startswith("postgres://"):
    # Render uses postgres:// but SQLAlchemy needs postgresql://
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# API Keys
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")

# Flask settings
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# News aggregation settings
NEWS_FETCH_DAYS = 7  # How many days back to search
MAX_ARTICLES_PER_SOURCE = 50  # Limit articles per RSS feed
DEDUP_THRESHOLD_HOURS = 24  # Consider duplicate if same person/company within this window

# Search queries for finding executive moves
SEARCH_QUERIES = [
    '"{company}" AND ("appointed" OR "promoted" OR "named" OR "joins" OR "hires")',
    '"{company}" AND ("CEO" OR "President" OR "Vice President" OR "VP" OR "Director" OR "Executive")',
    '"{company}" AND "executive" AND ("new" OR "announces")',
]

# LinkedIn post settings
MAX_POST_LENGTH = 3000  # LinkedIn character limit
DEFAULT_HASHTAGS = ["#MeatIndustry", "#PoultryIndustry", "#PeopleOnTheMove", "#Leadership"]

# Claude API settings
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 500

# Post generation system prompt
POST_SYSTEM_PROMPT = """You are a social media writer for Meatingplace, a publication for the meat and poultry industry.

Write a brief, factual LinkedIn post announcing an executive career move. Keep the tone straightforward and professional - not celebratory or upbeat. Simply state:
- Who the person is
- Their new title
- The company they're joining

Keep it to 1-2 short sentences. Include 2-3 relevant hashtags at the end.
Do not use exclamation points. Do not say "congratulations" or "excited" or similar celebratory language.
Do not make up details not provided in the input."""


def validate_config():
    """Check if required configuration is present."""
    warnings = []

    if not NEWSAPI_KEY:
        warnings.append("NEWSAPI_KEY not set - NewsAPI.org integration disabled")

    if not ANTHROPIC_API_KEY:
        warnings.append("ANTHROPIC_API_KEY not set - AI post generation disabled, using templates")

    return warnings
