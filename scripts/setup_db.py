#!/usr/bin/env python3
"""
Initialize the People on the Move database.
Creates all tables and optionally loads initial company data.
"""
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import DATABASE_URL, CONFIG_DIR
from src.database.models import get_engine, init_db, get_session, Company


def load_initial_companies(session, companies_file):
    """Load companies from JSON file."""
    with open(companies_file, 'r') as f:
        data = json.load(f)

    added = 0
    skipped = 0

    for company_data in data.get('companies', []):
        # Check if company already exists
        existing = session.query(Company).filter(
            Company.name == company_data['name']
        ).first()

        if existing:
            skipped += 1
            continue

        company = Company(
            name=company_data['name'],
            domain=company_data.get('domain'),
            website=company_data.get('website'),
        )
        if 'aliases' in company_data:
            company.set_aliases(company_data['aliases'])

        session.add(company)
        added += 1

    session.commit()
    return added, skipped


def main():
    """Initialize database and load initial data."""
    print("=" * 50)
    print("People on the Move - Database Setup")
    print("=" * 50)

    # Create database engine
    print(f"\nDatabase URL: {DATABASE_URL}")
    engine = get_engine(DATABASE_URL)

    # Create tables
    print("\nCreating database tables...")
    init_db(engine)
    print("  - companies")
    print("  - announcements")
    print("  - posts")
    print("Tables created successfully!")

    # Load initial companies
    companies_file = CONFIG_DIR / "companies.json"
    if companies_file.exists():
        print(f"\nLoading companies from {companies_file}...")
        session = get_session(engine)
        try:
            added, skipped = load_initial_companies(session, companies_file)
            print(f"  Added: {added} companies")
            print(f"  Skipped (already exist): {skipped} companies")
        finally:
            session.close()
    else:
        print(f"\nNo companies.json found at {companies_file}")
        print("You can import companies later using scripts/import_companies.py")

    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
