#!/usr/bin/env python3
"""
Import companies from a CSV file into the database.

Usage:
    python scripts/import_companies.py path/to/companies.csv

CSV format should have columns:
    - name (required): Company name
    - domain (optional): Email domain
    - website (optional): Company website URL
    - aliases (optional): Comma-separated alternative names
"""
import sys
import csv
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import click

from config.settings import DATABASE_URL, CONFIG_DIR
from src.database.models import get_engine, get_session, init_db, Company


def parse_aliases(alias_string):
    """Parse comma-separated aliases into a list."""
    if not alias_string:
        return []
    return [a.strip() for a in alias_string.split(',') if a.strip()]


def import_from_csv(session, csv_path):
    """Import companies from CSV file."""
    added = 0
    updated = 0
    skipped = 0

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        # Normalize column names (handle various casings)
        fieldnames = reader.fieldnames
        name_col = next((c for c in fieldnames if c.lower() in ['name', 'company', 'company_name']), None)
        domain_col = next((c for c in fieldnames if c.lower() in ['domain', 'email_domain']), None)
        website_col = next((c for c in fieldnames if c.lower() in ['website', 'url', 'company_url']), None)
        aliases_col = next((c for c in fieldnames if c.lower() in ['aliases', 'alias', 'other_names']), None)

        if not name_col:
            raise ValueError(f"CSV must have a 'name' or 'company' column. Found: {fieldnames}")

        for row in reader:
            name = row.get(name_col, '').strip()
            if not name:
                continue

            domain = row.get(domain_col, '').strip() if domain_col else None
            website = row.get(website_col, '').strip() if website_col else None
            aliases_str = row.get(aliases_col, '') if aliases_col else ''
            aliases = parse_aliases(aliases_str)

            # Check if company exists
            existing = session.query(Company).filter(Company.name == name).first()

            if existing:
                # Update if new data provided
                if domain and not existing.domain:
                    existing.domain = domain
                if website and not existing.website:
                    existing.website = website
                if aliases:
                    current = existing.get_aliases()
                    combined = list(set(current + aliases))
                    existing.set_aliases(combined)
                updated += 1
            else:
                # Create new company
                company = Company(
                    name=name,
                    domain=domain,
                    website=website,
                )
                if aliases:
                    company.set_aliases(aliases)
                session.add(company)
                added += 1

        session.commit()

    return added, updated, skipped


def import_from_json(session, json_path):
    """Import companies from JSON file."""
    with open(json_path, 'r') as f:
        data = json.load(f)

    added = 0
    skipped = 0

    for company_data in data.get('companies', []):
        name = company_data.get('name')
        if not name:
            continue

        existing = session.query(Company).filter(Company.name == name).first()
        if existing:
            skipped += 1
            continue

        company = Company(
            name=name,
            domain=company_data.get('domain'),
            website=company_data.get('website'),
        )
        if 'aliases' in company_data:
            company.set_aliases(company_data['aliases'])

        session.add(company)
        added += 1

    session.commit()
    return added, 0, skipped


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--update-json', is_flag=True, help='Also update config/companies.json')
def main(input_file, update_json):
    """Import companies from CSV or JSON file."""
    print("=" * 50)
    print("People on the Move - Company Import")
    print("=" * 50)

    input_path = Path(input_file)

    # Initialize database
    engine = get_engine(DATABASE_URL)
    init_db(engine)
    session = get_session(engine)

    try:
        # Determine file type and import
        if input_path.suffix.lower() == '.csv':
            print(f"\nImporting from CSV: {input_path}")
            added, updated, skipped = import_from_csv(session, input_path)
        elif input_path.suffix.lower() == '.json':
            print(f"\nImporting from JSON: {input_path}")
            added, updated, skipped = import_from_json(session, input_path)
        else:
            print(f"Error: Unsupported file type: {input_path.suffix}")
            print("Supported formats: .csv, .json")
            sys.exit(1)

        print(f"\nResults:")
        print(f"  Added: {added}")
        print(f"  Updated: {updated}")
        print(f"  Skipped: {skipped}")

        # Optionally update companies.json
        if update_json:
            print(f"\nUpdating {CONFIG_DIR / 'companies.json'}...")
            companies = session.query(Company).filter(Company.is_active == True).all()

            companies_data = {
                'companies': [
                    {
                        'name': c.name,
                        'domain': c.domain,
                        'website': c.website,
                        'aliases': c.get_aliases(),
                    }
                    for c in companies
                ]
            }

            with open(CONFIG_DIR / 'companies.json', 'w') as f:
                json.dump(companies_data, f, indent=2)

            print(f"  Updated with {len(companies)} companies")

        # Show total companies
        total = session.query(Company).count()
        print(f"\nTotal companies in database: {total}")

    finally:
        session.close()

    print("\n" + "=" * 50)
    print("Import complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
