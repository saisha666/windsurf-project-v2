# Roulette Data Scraper

Automated scraper for collecting roulette game data from multiple providers.

## Setup
1. Install Python 3.9+ if not installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

## Running the Scraper
```bash
python src/main.py
```

## Adding New Sites
1. Create a new provider configuration in `config/providers/`
2. Add site-specific scraping logic in `src/scrapers/providers/`
3. Update `config/sites.json` with the new site details

## Project Structure
- `src/` - Source code
- `config/` - Configuration files
- `data/` - Collected data
- `logs/` - Log files
- `tests/` - Test files
