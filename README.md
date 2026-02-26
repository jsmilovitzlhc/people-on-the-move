# People on the Move

A tool to aggregate executive job changes/promotions at meat industry companies, draft celebratory LinkedIn posts, and provide a review workflow for editors.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Initialize Database

```bash
python scripts/setup_db.py
```

### 4. Run the Aggregator

```bash
# Fetch news once
python scripts/run_aggregator.py --once

# Or run continuously (every hour)
python scripts/run_aggregator.py
```

### 5. Start the Dashboard

```bash
python -m src.dashboard.app
# Open http://localhost:5000
```

## Project Structure

```
PeopleOnTheMove/
├── config/
│   ├── companies.json       # Target companies list
│   └── settings.py          # Configuration
├── src/
│   ├── aggregator/          # News fetching & parsing
│   ├── database/            # SQLAlchemy models & operations
│   ├── drafting/            # Post generation (AI + templates)
│   └── dashboard/           # Flask web application
├── scripts/
│   ├── setup_db.py          # Initialize database
│   ├── import_companies.py  # Import companies from CSV
│   └── run_aggregator.py    # Main aggregator entry point
├── static/css/              # Dashboard styles
└── data/                    # SQLite database
```

## Configuration

### API Keys (Optional but Recommended)

| Service | Purpose | Get Key |
|---------|---------|---------|
| NewsAPI.org | Additional news sources | https://newsapi.org/register |
| Anthropic Claude | AI-powered post generation | https://console.anthropic.com |

Without API keys, the system uses:
- Google News RSS (no key required)
- Template-based post generation (fallback)

### Environment Variables

```bash
# .env file
NEWSAPI_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
FLASK_SECRET_KEY=random-secret-string
FLASK_DEBUG=true
```

## Usage

### Importing Companies

```bash
# From CSV
python scripts/import_companies.py data/companies.csv

# CSV format: name,domain,website,aliases
# Example: "Tyson Foods,tyson.com,https://tysonfoods.com,Tyson"
```

### Running the Aggregator

```bash
# Fetch news once
python scripts/run_aggregator.py --once

# Fetch for specific company
python scripts/run_aggregator.py --company "Tyson Foods" --once

# Continuous mode (hourly)
python scripts/run_aggregator.py --interval 3600
```

### Dashboard Workflow

1. **Review**: See pending announcements
2. **Edit**: Modify details or regenerate AI draft
3. **Approve**: Mark ready for posting
4. **Copy**: Copy post text to clipboard
5. **Post**: Paste to LinkedIn manually
6. **Mark Posted**: Record the LinkedIn URL

## News Sources

### Free (No API Key)
- Google News RSS
- PR Newswire RSS
- Business Wire RSS
- Industry publications (MeatPoultry.com, etc.)
- Company newsroom feeds

### With Free API Key
- NewsAPI.org (100 requests/day)

## Post Generation

The system uses Claude AI to generate natural, varied LinkedIn posts. If the API is unavailable, it falls back to template-based generation.

### AI System Prompt
> You are a social media writer for Meatingplace, the leading publication for the meat and poultry industry. Write a celebratory LinkedIn post about an executive career move...

## Database

SQLite database with three tables:

- **companies**: Tracked companies
- **announcements**: Executive moves found
- **posts**: Draft/published LinkedIn posts

## Development

```bash
# Run Flask in debug mode
FLASK_DEBUG=true python -m src.dashboard.app

# Check database
sqlite3 data/potm.db "SELECT * FROM announcements LIMIT 5;"
```

## License

Internal use - Meatingplace
