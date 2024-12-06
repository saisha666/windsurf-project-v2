import asyncio
import logging
from typing import Dict, List
from pathlib import Path
from datetime import datetime
import json
import psutil
import math

from .base_scraper import BaseScraper
from .providers.evolution_scraper import EvolutionScraper
from database.mongodb_handler import MongoDBHandler

class ScraperManager:
    def __init__(self, config: Dict):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.scrapers = []
        self.db_handler = MongoDBHandler(
            config['database']['connection_string'],
            config['database']['database_name']
        )
        
    async def check_system_resources(self):
        """Monitor system resources"""
        memory_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent()
        
        if memory_percent > self.config['scraper_settings']['memory_limit']:
            self.logger.warning(f"High memory usage: {memory_percent}%")
            return False
        if cpu_percent > self.config['scraper_settings']['cpu_limit']:
            self.logger.warning(f"High CPU usage: {cpu_percent}%")
            return False
        return True
        
    async def initialize_scrapers(self):
        """Initialize multiple scraper instances"""
        provider = self.config['providers']['evolution']
        browser_instances = self.config['scraper_settings']['browser_instances']
        tables_per_browser = self.config['scraper_settings']['tables_per_browser']
        
        try:
            # Load provider-specific configuration
            config_path = Path(__file__).parent.parent.parent / 'config' / 'providers' / provider['config_file']
            with open(config_path) as f:
                provider_config = json.load(f)
            
            # Split tables among browser instances
            total_tables = len(provider_config['tables'])
            tables_per_instance = math.ceil(total_tables / browser_instances)
            
            for i in range(browser_instances):
                start_idx = i * tables_per_instance
                end_idx = min((i + 1) * tables_per_instance, total_tables)
                
                instance_config = provider_config.copy()
                instance_config['tables'] = provider_config['tables'][start_idx:end_idx]
                
                scraper = EvolutionScraper(
                    instance_config,
                    self.db_handler,
                    self.config['scraper_settings']
                )
                self.scrapers.append(scraper)
                self.logger.info(f"Initialized scraper instance {i+1} with {len(instance_config['tables'])} tables")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize scrapers: {str(e)}")
    
    async def start(self):
        """Start all scraper instances"""
        await self.initialize_scrapers()
        
        while True:
            try:
                if not await self.check_system_resources():
                    await asyncio.sleep(30)  # Wait if system resources are stressed
                    continue
                
                # Start all scraper instances
                tasks = []
                for i, scraper in enumerate(self.scrapers):
                    task = asyncio.create_task(
                        scraper.run(self.config['providers']['evolution']['base_url'])
                    )
                    tasks.append(task)
                    # Stagger the start of each browser instance
                    await asyncio.sleep(self.config['providers']['evolution']['batch_delay'])
                
                # Wait for all scrapers to complete or fail
                await asyncio.gather(*tasks, return_exceptions=True)
                
            except Exception as e:
                self.logger.error(f"Error in scraper manager: {str(e)}")
                
            # Wait before retrying
            await asyncio.sleep(self.config['scraper_settings']['retry_interval'])
    
    def add_new_provider(self, provider_name: str, provider_config: Dict):
        """Add a new provider to the configuration"""
        try:
            # Update sites.json
            self.config['providers'][provider_name] = provider_config
            config_path = Path(__file__).parent.parent.parent / 'config' / 'sites.json'
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            # Create provider configuration file
            provider_config_path = Path(__file__).parent.parent.parent / 'config' / 'providers' / provider_config['config_file']
            with open(provider_config_path, 'w') as f:
                json.dump({}, f, indent=4)  # Create empty config file
                
            self.logger.info(f"Added new provider: {provider_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to add new provider {provider_name}: {str(e)}")
            raise
