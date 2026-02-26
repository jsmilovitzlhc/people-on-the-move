#!/usr/bin/env python3
"""
Import companies from the domain CSV file.
Maps domains to company names and filters out non-company domains.
"""
import sys
import csv
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import DATABASE_URL
from src.database.models import get_engine, get_session, init_db, Company

# Domains to skip (personal email, generic, etc.)
SKIP_DOMAINS = {
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
    'icloud.com', 'me.com', 'mac.com', 'live.com', 'msn.com',
    'sbcglobal.net', 'bellsouth.net', 'verizon.net', 'cox.net', 'comcast.net',
    'att.net', 'charter.net', 'earthlink.net', 'windstream.net',
    'ymail.com', 'protonmail.com', 'zoho.com',
    # Generic company/email domains
    'rogers.com',  # Telecom
}

# Domain to company name mapping
DOMAIN_TO_COMPANY = {
    'tyson.com': 'Tyson Foods',
    'cargill.com': 'Cargill',
    'smithfield.com': 'Smithfield Foods',
    'jbssa.com': 'JBS USA',
    'jbssa.com.au': 'JBS Australia',
    'hormel.com': 'Hormel Foods',
    'perdue.com': 'Perdue Farms',
    'pilgrims.com': "Pilgrim's Pride",
    'nationalbeef.com': 'National Beef',
    'americanfoodsgroup.com': 'American Foods Group',
    'usda.gov': 'USDA',
    'seaboardfoods.com': 'Seaboard Foods',
    'clemensfoodgroup.com': 'Clemens Food Group',
    'butterball.com': 'Butterball',
    'simfoods.com': 'Simmons Foods',
    'mountaire.com': 'Mountaire Farms',
    'kochfoods.com': 'Koch Foods',
    'sealedair.com': 'Sealed Air',
    'johnsonville.com': 'Johnsonville',
    'marel.com': 'Marel',
    'mapleleaf.com': 'Maple Leaf Foods',
    'j-ots.com': 'JOT Automation',
    'bunzlusa.com': 'Bunzl USA',
    'boarshead.com': "Boar's Head",
    'usfoods.com': 'US Foods',
    'greateromaha.com': 'Greater Omaha Packing',
    'waynefarms.com': 'Wayne Farms',
    'jbtc.com': 'JBT Corporation',
    'cooperfarms.com': 'Cooper Farms',
    'brakebush.com': 'Brakebush Brothers',
    'multivac.com': 'Multivac',
    'osigroup.com': 'OSI Group',
    'bar-s.com': 'Bar-S Foods',
    'jacklinks.com': "Jack Link's",
    'waynesanderson.com': 'Wayne-Sanderson Farms',
    'wolverinepacking.com': 'Wolverine Packing',
    'fosterfarms.com': 'Foster Farms',
    'vincitgroup.com': 'Vincit Group',
    'fieldale.com': 'Fieldale Farms',
    'georgesinc.com': "George's Inc",
    'freshmark.com': 'Freshmark',
    'pssi.com': 'PSSI',
    'pecofoods.com': 'Peco Foods',
    'reiser.com': 'Reiser',
    'sandersonfarms.com': 'Sanderson Farms',
    'darlingii.com': 'Darling Ingredients',
    'sugar-creek.com': 'Sugar Creek',
    'heb.com': 'H-E-B',
    'amickfarms.com': 'Amick Farms',
    'provisur.com': 'Provisur Technologies',
    'wholestonefarms.com': 'Wholestone Farms',
    'wlfoods.com': 'WL Foods',
    'jsfoods.com': 'JS Foods',
    'walmart.com': 'Walmart',
    'bellandevans.com': 'Bell & Evans',
    'beef.org': 'National Cattlemen\'s Beef Association',
    'benekeith.com': 'Ben E. Keith',
    'landofrost.com': 'Land O\'Frost',
    'costco.com': 'Costco',
    'kayem.com': 'Kayem Foods',
    'omahasteaks.com': 'Omaha Steaks',
    'intralox.com': 'Intralox',
    'houseofraeford.com': 'House of Raeford',
    'cfpbeef.com': 'Central Beef',
    'brucepac.com': 'BrucePac',
    'casefarms.com': 'Case Farms',
    'buddig.com': 'Carl Buddig',
    'amcor.com': 'Amcor',
    'nor-am.com': 'Nor-Am Cold Storage',
    'fsis.usda.gov': 'USDA FSIS',
    'monogramfoods.com': 'Monogram Foods',
    'triumphfoods.com': 'Triumph Foods',
    'conagra.com': 'Conagra Brands',
    'mapleleaffarms.com': 'Maple Leaf Farms',
    'hylife.com': 'HyLife',
    'harrisranchbeef.com': 'Harris Ranch Beef',
    'dawnfarms.ie': 'Dawn Farms',
    'goldcreekfoods.com': 'Gold Creek Foods',
    'miniat.com': 'Ed Miniat',
    'americold.com': 'Americold',
    'safefoods.net': 'Safe Foods',
    'ecolab.com': 'Ecolab',
    'conestogameats.com': 'Conestoga Meats',
    'olymel.com': 'Olymel',
    'kerry.com': 'Kerry Group',
    'bwfoods.com': 'BW Foods',
    'agribeef.com': 'Agri Beef',
    'handtmann.us': 'Handtmann',
    'gostampede.com': 'Stampede Culinary Partners',
    'farbestfoods.com': 'Farbest Foods',
    'merck.com': 'Merck Animal Health',
    'hantover.com': 'Hantover',
    'essentiaproteins.com': 'Essentia Protein Solutions',
    'coloradopremium.com': 'Colorado Premium',
    'pfgc.com': 'Performance Food Group',
    'meyerfoods.com': 'Meyer Foods',
    'okfoods.com': 'OK Foods',
    'aviagen.com': 'Aviagen',
    'empiricalfoods.com': 'Empirical Foods',
    'sysco.com': 'Sysco',
    'millerpoultry.com': 'Miller Poultry',
    'farmerfocus.com': 'Farmer Focus',
    'marubeni.com': 'Marubeni',
    'winpak.com': 'Winpak',
    'applegate.com': 'Applegate Farms',
    'nimanranch.com': 'Niman Ranch',
    'meatinstitute.org': 'Meat Institute',
    'elancoah.com': 'Elanco Animal Health',
    'superiorfarms.com': 'Superior Farms',
    'cardinalmeats.com': 'Cardinal Meats',
    'thomasfoodsusa.com': 'Thomas Foods USA',
    'sofinafoods.com': 'Sofina Foods',
    'pillers.com': "Piller's",
    'smartchicken.com': 'Smart Chicken',
    'hogslat.com': 'Hog Slat',
    'abfoodsusa.com': 'AB Foods USA',
    'nueske.com': "Nueske's",
    'cactusfeeders.com': 'Cactus Feeders',
    'pssi.co': 'PSSI',
    'wholefoods.com': 'Whole Foods Market',
    'prestagefoods.com': 'Prestage Foods',
    'cloverdalefoods.com': 'Cloverdale Foods',
    'gfs.com': 'Gordon Food Service',
    'corbion.com': 'Corbion',
    'kqf.com': 'KQF',
    'newlywedsfoods.com': 'Newly Weds Foods',
    'nipponham.co.jp': 'Nippon Ham',
    'prestagefarms.com': 'Prestage Farms',
    'greatrangebison.com': 'Great Range Bison',
    'pork.org': 'National Pork Board',
    'fplfood.com': 'FPL Food',
    'dailysmeats.com': "Daily's Premium Meats",
    'standardmeat.com': 'Standard Meat',
    'christensenfarms.com': 'Christensen Farms',
    'swaggertys.com': "Swaggerty's Farm",
    'leidys.com': "Leidy's",
    'dfequip.com': 'DF Equipment',
    'airgas.com': 'Airgas',
    'devro.com': 'Devro',
    'pigsrus.net': 'Pigs R Us',
    'miturkey.com': 'Michigan Turkey Producers',
    'marlen.com': 'Marlen International',
    'lopezfoods.com': 'Lopez Foods',
    'godshalls.com': "Godshall's",
    'startkleen.com': 'Starkleen',
    'oldtrapper.com': 'Old Trapper',
    'cavinessbeef.com': 'Caviness Beef Packers',
    'zoetis.com': 'Zoetis',
    'bih-us.com': 'BIH',
    'kiolbassa.com': 'Kiolbassa',
    'harpak-ulma.com': 'Harpak-ULMA',
    'gea.com': 'GEA Group',
    'elanco.com': 'Elanco',
    'nbeef.com': 'Nebraska Beef',
    'kroger.com': 'Kroger',
    'mitsubishicorp.com': 'Mitsubishi Corporation',
    'teysaust.com.au': 'Teys Australia',
    'effem.com': 'Mars Petcare',
    'weberweb.com': 'Weber',
    'baader.com': 'Baader',
    'buckheadmeat.com': 'Buckhead Meat',
    'claxtonpoultry.com': 'Claxton Poultry',
    'pfnmeats.com': 'PFN Meats',
    'inpac.com': 'Inpac',
    'stfmail.com': 'STF',
}


def get_company_name(domain):
    """Get company name from domain, or generate one."""
    if domain in DOMAIN_TO_COMPANY:
        return DOMAIN_TO_COMPANY[domain]

    # Generate name from domain
    name = domain.replace('.com', '').replace('.net', '').replace('.org', '')
    name = name.replace('.co', '').replace('.us', '').replace('.au', '')
    # Capitalize
    words = name.split('.')
    name = words[0]
    # Convert to title case
    return name.title().replace('Usa', 'USA').replace('Jbs', 'JBS')


def should_skip_domain(domain):
    """Check if domain should be skipped."""
    if domain in SKIP_DOMAINS:
        return True
    # Skip educational institutions
    if '.edu' in domain:
        return True
    # Skip government (except USDA)
    if '.gov' in domain and 'usda' not in domain:
        return True
    return False


def main():
    csv_path = project_root / "Delivery By Receiving Domain (3).csv"

    print("=" * 50)
    print("Importing companies from domain CSV")
    print("=" * 50)

    # Initialize database
    engine = get_engine(DATABASE_URL)
    init_db(engine)
    session = get_session(engine)

    added = 0
    skipped = 0
    already_exists = 0

    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                domain = row.get('domains1', '').strip().lower()

                if not domain:
                    continue

                if should_skip_domain(domain):
                    skipped += 1
                    continue

                company_name = get_company_name(domain)

                # Check if already exists
                existing = session.query(Company).filter(
                    (Company.name == company_name) | (Company.domain == domain)
                ).first()

                if existing:
                    already_exists += 1
                    continue

                # Add company
                company = Company(
                    name=company_name,
                    domain=domain,
                    website=f"https://www.{domain}",
                )
                session.add(company)
                added += 1
                print(f"  Added: {company_name} ({domain})")

        session.commit()

        print(f"\nResults:")
        print(f"  Added: {added}")
        print(f"  Already exist: {already_exists}")
        print(f"  Skipped (non-company): {skipped}")

        total = session.query(Company).count()
        print(f"\nTotal companies in database: {total}")

    finally:
        session.close()

    print("\n" + "=" * 50)
    print("Import complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
