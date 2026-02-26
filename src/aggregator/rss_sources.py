"""
RSS feed source definitions for People on the Move.
"""

# Google News RSS search (free, no API key required)
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

# PR Newswire feeds
PR_NEWSWIRE_FEEDS = [
    {
        "name": "PR Newswire - Food & Beverage",
        "url": "https://www.prnewswire.com/rss/food-and-beverages-industry-news.rss",
        "category": "industry_news"
    },
    {
        "name": "PR Newswire - Personnel Announcements",
        "url": "https://www.prnewswire.com/rss/personnel-announcements-news.rss",
        "category": "personnel"
    },
]

# Business Wire feeds
BUSINESS_WIRE_FEEDS = [
    {
        "name": "Business Wire - Food & Beverage",
        "url": "https://feed.businesswire.com/rss/home/?rss=G1QFDERJXkJeGVpXWg==",
        "category": "industry_news"
    },
]

# Industry-specific feeds
INDUSTRY_FEEDS = [
    {
        "name": "MeatPoultry.com - People",
        "url": "https://www.meatpoultry.com/rss/topic/285-people",
        "category": "personnel"
    },
    {
        "name": "MeatPoultry.com - All",
        "url": "https://www.meatpoultry.com/rss/topic/280-news",
        "category": "industry_news"
    },
    {
        "name": "The National Provisioner",
        "url": "https://www.provisioneronline.com/rss",
        "category": "industry_news"
    },
    {
        "name": "Food Business News",
        "url": "https://www.foodbusinessnews.net/rss",
        "category": "industry_news"
    },
    {
        "name": "Food Dive",
        "url": "https://www.fooddive.com/feeds/news/",
        "category": "industry_news"
    },
    {
        "name": "Grocery Dive",
        "url": "https://www.grocerydive.com/feeds/news/",
        "category": "industry_news"
    },
    {
        "name": "Supermarket News",
        "url": "https://www.supermarketnews.com/rss.xml",
        "category": "industry_news"
    },
    {
        "name": "Progressive Grocer",
        "url": "https://progressivegrocer.com/rss.xml",
        "category": "industry_news"
    },
    {
        "name": "Watt Poultry",
        "url": "https://www.wattagnet.com/rss/poultry",
        "category": "industry_news"
    },
    {
        "name": "Feedstuffs",
        "url": "https://www.feedstuffs.com/rss.xml",
        "category": "industry_news"
    },
]

# Company newsroom RSS feeds (if available)
COMPANY_NEWSROOMS = {
    "Tyson Foods": "https://ir.tyson.com/rss/news-releases.xml",
    "Hormel Foods": "https://www.hormelfoods.com/newsroom/feed/",
    "Smithfield Foods": "https://www.smithfieldfoods.com/press-room/feed",
    "Cargill": "https://www.cargill.com/feed/news",
    "JBS USA": "https://jbsfoodsgroup.com/feed",
    "Maple Leaf Foods": "https://www.mapleleaffoods.com/feed/",
    "Conagra Brands": "https://www.conagrabrands.com/news-room/rss",
    "Sysco": "https://investors.sysco.com/rss/news-releases.xml",
    "US Foods": "https://ir.usfoods.com/rss/news-releases.xml",
    "Kroger": "https://ir.kroger.com/rss/news-releases.xml",
    "Walmart": "https://corporate.walmart.com/feeds/news",
}

# PR Newswire company-specific news pages
# These are HTML pages that need to be scraped (no RSS available)
# URL format: https://www.prnewswire.com/news/{company-slug}/
PR_NEWSWIRE_COMPANIES = {
    # Major meat & poultry processors
    "Tyson Foods": "https://www.prnewswire.com/news/tyson-foods-inc/",
    "Hormel Foods": "https://www.prnewswire.com/news/hormel-foods-corporation/",
    "Smithfield Foods": "https://www.prnewswire.com/news/smithfield-foods-inc/",
    "Cargill": "https://www.prnewswire.com/news/cargill/",
    "JBS USA": "https://www.prnewswire.com/news/jbs-usa/",
    "Pilgrim's Pride": "https://www.prnewswire.com/news/pilgrims-pride-corporation/",
    "Perdue Farms": "https://www.prnewswire.com/news/perdue-farms/",
    "Sanderson Farms": "https://www.prnewswire.com/news/sanderson-farms/",
    "National Beef": "https://www.prnewswire.com/news/national-beef-packing-company/",
    "Seaboard Foods": "https://www.prnewswire.com/news/seaboard-foods/",
    "Conagra Brands": "https://www.prnewswire.com/news/conagra-brands,-inc./",
    "Sysco": "https://www.prnewswire.com/news/sysco-corporation/",
    "US Foods": "https://www.prnewswire.com/news/us-foods-holding-corp/",
    "Kroger": "https://www.prnewswire.com/news/the-kroger-co/",
    # Additional companies from CSV
    "American Foods Group": "https://www.prnewswire.com/news/american-foods-group/",
    "Clemens Food Group": "https://www.prnewswire.com/news/clemens-food-group/",
    "Butterball": "https://www.prnewswire.com/news/butterball-llc/",
    "Simmons Foods": "https://www.prnewswire.com/news/simmons-foods/",
    "Mountaire Farms": "https://www.prnewswire.com/news/mountaire-farms/",
    "Koch Foods": "https://www.prnewswire.com/news/koch-foods/",
    "Sealed Air": "https://www.prnewswire.com/news/sealed-air-corporation/",
    "Johnsonville": "https://www.prnewswire.com/news/johnsonville-sausage-llc/",
    "Marel": "https://www.prnewswire.com/news/marel/",
    "Maple Leaf Foods": "https://www.prnewswire.com/news/maple-leaf-foods-inc/",
    "Boar's Head": "https://www.prnewswire.com/news/boars-head/",
    "Greater Omaha Packing": "https://www.prnewswire.com/news/greater-omaha-packing/",
    "Wayne Farms": "https://www.prnewswire.com/news/wayne-farms-llc/",
    "Wayne-Sanderson Farms": "https://www.prnewswire.com/news/wayne-sanderson-farms/",
    "Cooper Farms": "https://www.prnewswire.com/news/cooper-farms/",
    "Brakebush": "https://www.prnewswire.com/news/brakebush-brothers/",
    "Multivac": "https://www.prnewswire.com/news/multivac/",
    "OSI Group": "https://www.prnewswire.com/news/osi-group/",
    "Bar-S Foods": "https://www.prnewswire.com/news/bar-s-foods/",
    "Jack Link's": "https://www.prnewswire.com/news/jack-links/",
    "Wolverine Packing": "https://www.prnewswire.com/news/wolverine-packing-company/",
    "Foster Farms": "https://www.prnewswire.com/news/foster-farms/",
    "Fieldale Farms": "https://www.prnewswire.com/news/fieldale-farms/",
    "George's": "https://www.prnewswire.com/news/georges-inc/",
    "Peco Foods": "https://www.prnewswire.com/news/peco-foods/",
    "Darling Ingredients": "https://www.prnewswire.com/news/darling-ingredients-inc/",
    "Sugar Creek": "https://www.prnewswire.com/news/sugar-creek-packing/",
    "H-E-B": "https://www.prnewswire.com/news/h-e-b/",
    "Amick Farms": "https://www.prnewswire.com/news/amick-farms/",
    "Provisur Technologies": "https://www.prnewswire.com/news/provisur-technologies/",
    "Wholestone Farms": "https://www.prnewswire.com/news/wholestone-farms/",
    "Bell & Evans": "https://www.prnewswire.com/news/bell-evans/",
    "Land O'Frost": "https://www.prnewswire.com/news/land-o-frost/",
    "Costco": "https://www.prnewswire.com/news/costco-wholesale-corporation/",
    "Kayem Foods": "https://www.prnewswire.com/news/kayem-foods/",
    "Omaha Steaks": "https://www.prnewswire.com/news/omaha-steaks/",
    "Intralox": "https://www.prnewswire.com/news/intralox/",
    "House of Raeford": "https://www.prnewswire.com/news/house-of-raeford-farms/",
    "BrucePac": "https://www.prnewswire.com/news/brucepac/",
    "Case Farms": "https://www.prnewswire.com/news/case-farms/",
    "Buddig": "https://www.prnewswire.com/news/carl-buddig-company/",
    "Amcor": "https://www.prnewswire.com/news/amcor/",
    "Monogram Foods": "https://www.prnewswire.com/news/monogram-foods/",
    "Triumph Foods": "https://www.prnewswire.com/news/triumph-foods/",
    "Maple Leaf Farms": "https://www.prnewswire.com/news/maple-leaf-farms/",
    "Hylife": "https://www.prnewswire.com/news/hylife/",
    "Harris Ranch Beef": "https://www.prnewswire.com/news/harris-ranch-beef-company/",
    "Gold Creek Foods": "https://www.prnewswire.com/news/gold-creek-foods/",
    "Americold": "https://www.prnewswire.com/news/americold-realty-trust/",
    "Ecolab": "https://www.prnewswire.com/news/ecolab-inc/",
    "Olymel": "https://www.prnewswire.com/news/olymel/",
    "Kerry Group": "https://www.prnewswire.com/news/kerry-group/",
    "Agri Beef": "https://www.prnewswire.com/news/agri-beef-co/",
    "Farbest Foods": "https://www.prnewswire.com/news/farbest-foods/",
    "Merck Animal Health": "https://www.prnewswire.com/news/merck-animal-health/",
    "Colorado Premium": "https://www.prnewswire.com/news/colorado-premium/",
    "Performance Food Group": "https://www.prnewswire.com/news/performance-food-group-company/",
    "OK Foods": "https://www.prnewswire.com/news/ok-foods/",
    "Aviagen": "https://www.prnewswire.com/news/aviagen/",
    "Applegate": "https://www.prnewswire.com/news/applegate/",
    "Niman Ranch": "https://www.prnewswire.com/news/niman-ranch/",
    "Elanco": "https://www.prnewswire.com/news/elanco-animal-health/",
    "Superior Farms": "https://www.prnewswire.com/news/superior-farms/",
    "Sofina Foods": "https://www.prnewswire.com/news/sofina-foods/",
    "Piller's": "https://www.prnewswire.com/news/pillers/",
    "Prestage Foods": "https://www.prnewswire.com/news/prestage-foods/",
    "Gordon Food Service": "https://www.prnewswire.com/news/gordon-food-service/",
    "Corbion": "https://www.prnewswire.com/news/corbion/",
    "Newlyweds Foods": "https://www.prnewswire.com/news/newlyweds-foods/",
    "Nippon Ham": "https://www.prnewswire.com/news/nippon-ham/",
    "Zoetis": "https://www.prnewswire.com/news/zoetis/",
    "Whole Foods Market": "https://www.prnewswire.com/news/whole-foods-market/",
    "Cloverdale Foods": "https://www.prnewswire.com/news/cloverdale-foods/",
    "Christensen Farms": "https://www.prnewswire.com/news/christensen-farms/",
    "Devro": "https://www.prnewswire.com/news/devro/",
    "Claxton Poultry": "https://www.prnewswire.com/news/claxton-poultry/",
    "GEA Group": "https://www.prnewswire.com/news/gea-group/",
    "Walmart": "https://www.prnewswire.com/news/walmart-inc/",
    "McDonald's": "https://www.prnewswire.com/news/mcdonalds-corporation/",
    "Marubeni": "https://www.prnewswire.com/news/marubeni-corporation/",
    "Winpak": "https://www.prnewswire.com/news/winpak/",
}

# Domain to company name mapping for looking up companies by email domain
DOMAIN_TO_COMPANY = {
    "tyson.com": "Tyson Foods",
    "cargill.com": "Cargill",
    "smithfield.com": "Smithfield Foods",
    "smithfieldfoods.com": "Smithfield Foods",
    "jbssa.com": "JBS USA",
    "jbssa.com.au": "JBS USA",
    "hormel.com": "Hormel Foods",
    "hormelfoods.com": "Hormel Foods",
    "perdue.com": "Perdue Farms",
    "pilgrims.com": "Pilgrim's Pride",
    "nationalbeef.com": "National Beef",
    "americanfoodsgroup.com": "American Foods Group",
    "seaboardfoods.com": "Seaboard Foods",
    "clemensfoodgroup.com": "Clemens Food Group",
    "butterball.com": "Butterball",
    "simfoods.com": "Simmons Foods",
    "mountaire.com": "Mountaire Farms",
    "kochfoods.com": "Koch Foods",
    "sealedair.com": "Sealed Air",
    "johnsonville.com": "Johnsonville",
    "marel.com": "Marel",
    "mapleleaf.com": "Maple Leaf Foods",
    "boarshead.com": "Boar's Head",
    "usfoods.com": "US Foods",
    "greateromaha.com": "Greater Omaha Packing",
    "waynefarms.com": "Wayne Farms",
    "waynesanderson.com": "Wayne-Sanderson Farms",
    "cooperfarms.com": "Cooper Farms",
    "brakebush.com": "Brakebush",
    "multivac.com": "Multivac",
    "osigroup.com": "OSI Group",
    "bar-s.com": "Bar-S Foods",
    "jacklinks.com": "Jack Link's",
    "wolverinepacking.com": "Wolverine Packing",
    "fosterfarms.com": "Foster Farms",
    "fieldale.com": "Fieldale Farms",
    "georgesinc.com": "George's",
    "pecofoods.com": "Peco Foods",
    "sandersonfarms.com": "Sanderson Farms",
    "darlingii.com": "Darling Ingredients",
    "sugar-creek.com": "Sugar Creek",
    "heb.com": "H-E-B",
    "amickfarms.com": "Amick Farms",
    "provisur.com": "Provisur Technologies",
    "wholestonefarms.com": "Wholestone Farms",
    "bellandevans.com": "Bell & Evans",
    "landofrost.com": "Land O'Frost",
    "costco.com": "Costco",
    "kayem.com": "Kayem Foods",
    "omahasteaks.com": "Omaha Steaks",
    "intralox.com": "Intralox",
    "houseofraeford.com": "House of Raeford",
    "brucepac.com": "BrucePac",
    "casefarms.com": "Case Farms",
    "buddig.com": "Buddig",
    "amcor.com": "Amcor",
    "monogramfoods.com": "Monogram Foods",
    "triumphfoods.com": "Triumph Foods",
    "conagra.com": "Conagra Brands",
    "mapleleaffarms.com": "Maple Leaf Farms",
    "hylife.com": "Hylife",
    "harrisranchbeef.com": "Harris Ranch Beef",
    "goldcreekfoods.com": "Gold Creek Foods",
    "americold.com": "Americold",
    "ecolab.com": "Ecolab",
    "olymel.com": "Olymel",
    "kerry.com": "Kerry Group",
    "agribeef.com": "Agri Beef",
    "farbestfoods.com": "Farbest Foods",
    "merck.com": "Merck Animal Health",
    "coloradopremium.com": "Colorado Premium",
    "pfgc.com": "Performance Food Group",
    "okfoods.com": "OK Foods",
    "aviagen.com": "Aviagen",
    "applegate.com": "Applegate",
    "nimanranch.com": "Niman Ranch",
    "elanco.com": "Elanco",
    "elancoah.com": "Elanco",
    "superiorfarms.com": "Superior Farms",
    "sofinafoods.com": "Sofina Foods",
    "pillers.com": "Piller's",
    "prestagefoods.com": "Prestage Foods",
    "prestagefarms.com": "Prestage Foods",
    "gfs.com": "Gordon Food Service",
    "corbion.com": "Corbion",
    "newlywedsfoods.com": "Newlyweds Foods",
    "nipponham.co.jp": "Nippon Ham",
    "zoetis.com": "Zoetis",
    "wholefoods.com": "Whole Foods Market",
    "cloverdalefoods.com": "Cloverdale Foods",
    "christensenfarms.com": "Christensen Farms",
    "devro.com": "Devro",
    "claxtonpoultry.com": "Claxton Poultry",
    "gea.com": "GEA Group",
    "walmart.com": "Walmart",
    "us.mcd.com": "McDonald's",
    "marubeni.com": "Marubeni",
    "winpak.com": "Winpak",
    "sysco.com": "Sysco",
    "corp.sysco.com": "Sysco",
    "kroger.com": "Kroger",
}


def get_prnewswire_company_url(company_name: str) -> str:
    """Get PR Newswire company page URL if available."""
    return PR_NEWSWIRE_COMPANIES.get(company_name)


def get_company_name_from_domain(domain: str) -> str:
    """Get company name from email domain."""
    return DOMAIN_TO_COMPANY.get(domain)

# Search queries for finding executive moves via Google News
# Expanded to include VP and Director level positions
EXECUTIVE_MOVE_QUERIES = [
    '"{company}" appointed CEO',
    '"{company}" appointed president',
    '"{company}" names CEO',
    '"{company}" new CEO',
    '"{company}" promoted',
    '"{company}" hires',
    '"{company}" executive',
    '"{company}" leadership',
    '"{company}" announces',
    '"{company}" vice president',
    '"{company}" VP appointed',
    '"{company}" director appointed',
    '"{company}" names VP',
    '"{company}" SVP',
    '"{company}" chief officer',
]

# Keywords that indicate an article is about an executive move
EXECUTIVE_KEYWORDS = [
    "appointed",
    "promoted",
    "named",
    "joins",
    "hires",
    "hired",
    "new ceo",
    "new president",
    "new chief",
    "new vp",
    "new vice president",
    "new director",
    "announces",
    "leadership",
    "executive",
    "succession",
    "steps down",
    "retires",
    "takes over",
    "taps",
    "elevates",
    "selects",
    "names",
    "appoints",
]

# Job titles to look for - expanded to include more VP/Director levels
EXECUTIVE_TITLES = [
    # C-Suite
    "CEO",
    "Chief Executive Officer",
    "President",
    "COO",
    "Chief Operating Officer",
    "CFO",
    "Chief Financial Officer",
    "CMO",
    "Chief Marketing Officer",
    "CTO",
    "Chief Technology Officer",
    "CIO",
    "Chief Information Officer",
    "CHRO",
    "Chief Human Resources Officer",
    "Chief Supply Chain Officer",
    "Chief Commercial Officer",
    "Chief Revenue Officer",
    "Chief Sales Officer",
    "Chief Strategy Officer",
    # VP Level
    "Vice President",
    "VP",
    "SVP",
    "Senior Vice President",
    "EVP",
    "Executive Vice President",
    "Group Vice President",
    "Regional Vice President",
    "VP of Sales",
    "VP of Marketing",
    "VP of Operations",
    "VP of Finance",
    "VP of Human Resources",
    "VP of Supply Chain",
    "VP of Manufacturing",
    "VP of Procurement",
    "VP of Quality",
    "VP of R&D",
    "VP of Research",
    # Director Level
    "Director",
    "Senior Director",
    "Executive Director",
    "Managing Director",
    "Regional Director",
    "Director of Sales",
    "Director of Marketing",
    "Director of Operations",
    "Director of Finance",
    # General Management
    "General Manager",
    "Plant Manager",
    "Division President",
    "Business Unit President",
    # Board
    "Chairman",
    "Board Member",
    "Board Director",
]


def get_all_rss_feeds():
    """Return all configured RSS feeds."""
    feeds = []
    feeds.extend(PR_NEWSWIRE_FEEDS)
    feeds.extend(BUSINESS_WIRE_FEEDS)
    feeds.extend(INDUSTRY_FEEDS)
    return feeds


def build_google_news_url(company_name: str, query_template: str = None) -> str:
    """Build a Google News RSS search URL for a company."""
    import urllib.parse

    if query_template:
        query = query_template.format(company=company_name)
    else:
        # Default query for executive moves
        query = f'"{company_name}" AND (appointed OR promoted OR named OR joins)'

    encoded_query = urllib.parse.quote(query)
    return GOOGLE_NEWS_RSS.format(query=encoded_query)


def get_company_newsroom_feed(company_name: str) -> str:
    """Get company-specific newsroom RSS feed if available."""
    return COMPANY_NEWSROOMS.get(company_name)
