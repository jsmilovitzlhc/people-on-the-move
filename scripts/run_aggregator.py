#!/usr/bin/env python3
"""
Run the news aggregator to fetch executive move announcements.

Usage:
    python scripts/run_aggregator.py           # Fetch for all companies
    python scripts/run_aggregator.py --once    # Run once and exit
    python scripts/run_aggregator.py --company "Tyson Foods"  # Specific company
"""
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import click

from config import settings
from src.database.models import get_engine, get_session, init_db
from src.database import operations as db_ops
from src.aggregator.news_fetcher import NewsAggregator
from src.drafting.ai_generator import generate_post

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_companies_from_db(session):
    """Load companies from database as dicts for aggregator."""
    companies = db_ops.get_active_companies(session)
    return [
        {
            'id': c.id,
            'name': c.name,
            'domain': c.domain,
            'aliases': c.get_aliases(),
        }
        for c in companies
    ]


def save_announcement(session, ann_data, auto_draft=True, max_age_days=None):
    """
    Save an announcement to the database.

    Args:
        session: Database session
        ann_data: Dict with announcement data from aggregator
        auto_draft: If True, automatically generate draft post
        max_age_days: If set, skip announcements older than this

    Returns:
        True if saved, False if duplicate or invalid
    """
    # Skip entries without a person name (required field)
    if not ann_data.get('person_name'):
        logger.debug(f"Skipping entry without person name: {ann_data.get('source_url')}")
        return False

    # Skip entries older than max_age_days
    if max_age_days and ann_data.get('announcement_date'):
        from datetime import timedelta
        cutoff = datetime.now().date() - timedelta(days=max_age_days)
        ann_date = ann_data['announcement_date']
        if ann_date < cutoff:
            logger.debug(f"Skipping old announcement ({ann_date}): {ann_data.get('person_name')}")
            return False

    # Check for duplicates
    existing = db_ops.check_duplicate(
        session,
        company_id=ann_data['company_id'],
        person_name=ann_data.get('person_name', ''),
        hours=settings.DEDUP_THRESHOLD_HOURS
    )

    if existing:
        logger.debug(f"Skipping duplicate: {ann_data.get('person_name')} at {ann_data.get('company_name')}")
        return False

    # Create announcement
    announcement = db_ops.create_announcement(
        session,
        company_id=ann_data['company_id'],
        person_name=ann_data.get('person_name'),
        new_title=ann_data.get('new_title'),
        announcement_date=ann_data.get('announcement_date'),
        source_url=ann_data.get('source_url'),
        source_name=ann_data.get('source_name'),
        raw_text=ann_data.get('raw_text'),
    )

    logger.info(f"Saved: {ann_data.get('person_name')} - {ann_data.get('new_title')} at {ann_data.get('company_name')}")

    # Auto-generate draft post
    if auto_draft:
        try:
            draft_content = generate_post(ann_data, use_ai=True)
            db_ops.create_post(session, announcement.id, draft_content)
            logger.debug(f"Generated draft post for announcement {announcement.id}")
        except Exception as e:
            logger.warning(f"Failed to generate draft post: {e}")

    return True


def run_aggregation(session, companies, days_back=7, company_filter=None):
    """
    Run the aggregation process.

    Args:
        session: Database session
        companies: List of company dicts
        days_back: How many days of news to fetch
        company_filter: Optional company name to filter

    Returns:
        Tuple of (new_count, duplicate_count)
    """
    # Filter companies if specified
    if company_filter:
        companies = [c for c in companies if company_filter.lower() in c['name'].lower()]
        if not companies:
            logger.error(f"No company found matching: {company_filter}")
            return 0, 0

    logger.info(f"Starting aggregation for {len(companies)} companies...")

    aggregator = NewsAggregator(companies)
    announcements = aggregator.fetch_all(days_back=days_back)

    new_count = 0
    dup_count = 0

    for ann in announcements:
        if save_announcement(session, ann, max_age_days=days_back):
            new_count += 1
        else:
            dup_count += 1

    return new_count, dup_count


@click.command()
@click.option('--once', is_flag=True, help='Run once and exit')
@click.option('--days', default=7, help='Days of news to fetch')
@click.option('--company', help='Filter to specific company')
@click.option('--interval', default=3600, help='Seconds between runs (when not using --once)')
@click.option('--no-draft', is_flag=True, help='Skip auto-generating draft posts')
def main(once, days, company, interval, no_draft):
    """Run the news aggregator."""
    print("=" * 50)
    print("People on the Move - News Aggregator")
    print("=" * 50)

    # Validate configuration
    warnings = settings.validate_config()
    for warning in warnings:
        logger.warning(warning)

    # Initialize database
    engine = get_engine(settings.DATABASE_URL)
    init_db(engine)

    while True:
        session = get_session(engine)
        try:
            # Load companies
            companies = get_companies_from_db(session)

            if not companies:
                logger.error("No companies found in database. Run setup_db.py first.")
                break

            logger.info(f"Loaded {len(companies)} companies from database")

            # Run aggregation
            start_time = datetime.now()
            new_count, dup_count = run_aggregation(
                session,
                companies,
                days_back=days,
                company_filter=company
            )
            elapsed = (datetime.now() - start_time).total_seconds()

            print(f"\n{'=' * 50}")
            print(f"Aggregation completed in {elapsed:.1f}s")
            print(f"  New announcements: {new_count}")
            print(f"  Duplicates skipped: {dup_count}")
            print(f"{'=' * 50}\n")

            if once:
                break

            logger.info(f"Sleeping for {interval} seconds...")
            time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error during aggregation: {e}")
            if once:
                raise
            logger.info(f"Retrying in {interval} seconds...")
            time.sleep(interval)
        finally:
            session.close()

    print("\nAggregator stopped.")


if __name__ == "__main__":
    main()
