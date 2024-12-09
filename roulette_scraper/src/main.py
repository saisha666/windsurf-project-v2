import asyncio
import json
import logging.config
from pathlib import Path
from datetime import datetime
from scrapers.scraper_manager import ScraperManager
from utils.logger import setup_logging

async def main():
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config_path = Path(__file__).parent.parent / 'config' / 'sites.json'
        with open(config_path) as f:
            config = json.load(f)
            
        # Initialize scraper manager
        manager = ScraperManager(config)
        
        # Start scraping
        logger.info("Starting roulette data collection...")
        await manager.start()
        
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
