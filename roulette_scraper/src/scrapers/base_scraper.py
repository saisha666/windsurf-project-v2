from abc import ABC, abstractmethod
import asyncio
import logging
from typing import Dict, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from datetime import datetime
import json

class BaseScraper(ABC):
    def __init__(self, config: Dict, db_handler, settings: Dict):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.db_handler = db_handler
        self.settings = settings
        self.playwright = None
        self.browser = None
        self.context = None
        self.data_buffer = []
    
    async def setup_browser(self):
        """Initialize browser with stealth settings"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=site-per-process',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-remote-fonts',
                '--disable-background-networking',
                '--disable-default-apps',
                '--disable-extensions',
                '--disable-sync',
                '--disable-translate',
                '--hide-scrollbars',
                '--metrics-recording-only',
                '--mute-audio',
                '--no-first-run',
                '--safebrowsing-disable-auto-update'
            ]
        )
        
        # Create context with optimized settings
        self.context = await self.browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            ignore_https_errors=True,
            java_script_enabled=True,
            bypass_csp=True
        )
        
        # Enhanced stealth scripts
        await self.context.add_init_script("""
            // Advanced stealth setup
            (() => {
                window.chrome = {
                    runtime: {},
                    loadTimes: function(){},
                    csi: function(){},
                    app: {},
                };
                
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {
                            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        }
                    ],
                });
                
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({state: Notification.permission}) :
                        originalQuery(parameters)
                );
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            })();
        """)
    
    @abstractmethod
    async def extract_data(self, page: Page) -> Optional[Dict]:
        """Extract data from the page - must be implemented by child classes"""
        pass
    
    async def save_data(self):
        """Save buffered data to database"""
        if self.data_buffer:
            try:
                await self.db_handler.insert_many(self.data_buffer)
                self.logger.info(f"Saved {len(self.data_buffer)} records to database")
                self.data_buffer = []
            except Exception as e:
                self.logger.error(f"Error saving data: {str(e)}")
    
    async def monitor_table(self, table_config: Dict):
        """Monitor a specific table"""
        page = await self.context.new_page()
        
        try:
            await page.goto(table_config['url'])
            while True:
                try:
                    data = await self.extract_data(page)
                    if data:
                        self.data_buffer.append(data)
                        
                        if len(self.data_buffer) >= self.settings['buffer_size']:
                            await self.save_data()
                            
                except Exception as e:
                    self.logger.error(f"Error monitoring table {table_config['description']}: {str(e)}")
                    await page.reload()
                
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Fatal error monitoring table {table_config['description']}: {str(e)}")
        finally:
            await page.close()
    
    async def run(self, base_url: str):
        """Run the scraper"""
        try:
            await self.setup_browser()
            
            # Start monitoring all tables
            tasks = []
            for table in self.config['tables']:
                table['url'] = f"{base_url}/{table['path']}"
                task = asyncio.create_task(self.monitor_table(table))
                tasks.append(task)
                await asyncio.sleep(2)  # Stagger table monitoring
            
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logger.error(f"Error in scraper: {str(e)}")
        finally:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
