from typing import Dict, Optional, List, Set
from playwright.async_api import Page, Request, Route, WebSocket, Browser
import logging
import json
from datetime import datetime
import asyncio
import re
import base64
from urllib.parse import urlparse, parse_qs
from src.scrapers.base_scraper import BaseScraper
import random
import aiohttp
import os
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class EvolutionScraper(BaseScraper):
    def __init__(self, config: Dict, db_handler, settings: Dict):
        super().__init__(config, db_handler, settings)
        
        # Track what we find
        self.discovered = {
            'endpoints': set(),    
            'websockets': set(),   
            'origins': set(),      
            'suppliers': set(),    
            'vue_states': set(),   
            'socket_messages': [], 
            'xhr_requests': []     
        }
        
        # Browser configurations
        self.browser_configs = {
            'undetected_chrome': {
                'name': 'Undetected Chrome',
                'version': '114.0.5735.90',  # Specific version known to work well
                'options': [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--start-maximized'
                ]
            },
            'brave': {
                'name': 'Brave',
                'binary_location': 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe',
                'options': [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage'
                ]
            },
            'firefox': {
                'name': 'Firefox',
                'options': [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage'
                ]
            }
        }
        
        # ChromeDriver versions to try
        self.chrome_versions = [
            '114.0.5735.90',
            '113.0.5672.63',
            '112.0.5615.49',
            '111.0.5563.64',
            '110.0.5481.77'
        ]
        
        # Scout mode settings
        self.scout_mode = True  # Start in scout mode
        self.recording = True   # Record network traffic
        self.har_path = "network_logs.har"
        
        # Extension paths
        self.extension_paths = {
            'vue_devtools': os.path.expanduser("~/.config/chromium/Default/Extensions/nhdogjmejiglipccpnnnanhbledajbpd"),
            'network_logger': os.path.expanduser("~/.config/chromium/Default/Extensions/network_logger")
        }
        
        # Connection tracking
        self.connections = {
            'active': set(),       # Active connections
            'successful': set(),   # Good connections
            'upstream': set()      # Potential upstream sources
        }
        
        # Browser profiles
        self.browser_profiles = [
            {
                "name": "Chrome Windows",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "viewport": {"width": 1920, "height": 1080},
                "platform": "Windows",
            },
            {
                "name": "Firefox Mac",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
                "viewport": {"width": 1440, "height": 900},
                "platform": "MacOS",
            },
            {
                "name": "Safari Mac",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
                "viewport": {"width": 1680, "height": 1050},
                "platform": "MacOS",
            }
        ]
        
        # Proxy list - starting with some test proxies
        self.proxies = [
            "http://103.152.112.162:80",
            "http://47.74.152.29:8888",
            "http://51.159.115.233:3128",
            None  # No proxy option as fallback
        ]
        
    async def get_random_browser_profile(self):
        """Get a random browser profile"""
        return random.choice(self.browser_profiles)
        
    async def get_random_proxy(self):
        """Get a random proxy"""
        return random.choice(self.proxies)
        
    async def setup_undetected_chrome(self):
        """Setup undetected-chromedriver"""
        print("Setting up undetected Chrome...")
        options = uc.ChromeOptions()
        
        # Add our stealth options
        for opt in self.browser_configs['undetected_chrome']['options']:
            options.add_argument(opt)
            
        # Use random Chrome version
        version = random.choice(self.chrome_versions)
        print(f"Using Chrome version: {version}")
        
        driver = uc.Chrome(
            version_main=int(version.split('.')[0]),  # Major version number
            options=options,
            driver_executable_path=f"drivers/chromedriver_{version}.exe",
            browser_executable_path=None,  # Let it find Chrome automatically
            suppress_welcome=True
        )
        
        return driver
        
    async def setup_brave(self):
        """Setup Brave browser"""
        print("Setting up Brave browser...")
        options = Options()
        options.binary_location = self.browser_configs['brave']['binary_location']
        
        for opt in self.browser_configs['brave']['options']:
            options.add_argument(opt)
            
        service = Service("drivers/chromedriver_brave.exe")
        driver = webdriver.Chrome(service=service, options=options)
        return driver
        
    async def setup_browser(self):
        """Setup browser with anti-detection measures"""
        try:
            # Randomly choose a browser type
            browser_type = random.choice(['undetected_chrome', 'brave'])
            print(f"Using browser: {self.browser_configs[browser_type]['name']}")
            
            if browser_type == 'undetected_chrome':
                self.driver = await self.setup_undetected_chrome()
            elif browser_type == 'brave':
                self.driver = await self.setup_brave()
                
            # Add additional stealth
            await self.inject_stealth_scripts()
            
            return True
            
        except Exception as e:
            print(f"Browser setup failed: {str(e)}")
            return False
            
    async def inject_stealth_scripts(self):
        """Inject various stealth scripts"""
        stealth_scripts = [
            # Navigator webdriver
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """,
            # Plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            """,
            # Chrome
            """
            window.chrome = {
                runtime: {}
            };
            """,
            # Permissions
            """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
            """
        ]
        
        for script in stealth_scripts:
            self.driver.execute_script(script)
            
    async def handle_request(self, route: Route):
        """Enhanced request handler with detailed logging"""
        request = route.request
        url = request.url
        
        if self.scout_mode:
            # Log interesting patterns
            if "socket" in url.lower():
                print(f"WebSocket attempt: {url}")
                self.discovered['websockets'].add(url)
                
            if request.resource_type == "xhr":
                print(f"XHR Request: {url}")
                self.discovered['xhr_requests'].append({
                    'url': url,
                    'method': request.method,
                    'headers': request.headers,
                    'time': datetime.now().isoformat()
                })
                
            # Look for Vue.js state updates
            if "vuex" in url.lower() or "state" in url.lower():
                print(f"Possible Vue state update: {url}")
                self.discovered['vue_states'].add(url)
                
        await route.continue_()
        
    async def analyze_websocket(self, ws: WebSocket):
        """Analyze WebSocket messages"""
        try:
            while True:
                msg = await ws.receive_text()
                print(f"WS Message: {msg[:200]}...")  # First 200 chars
                
                # Store interesting messages
                if any(key in msg.lower() for key in ['roulette', 'game', 'bet', 'result']):
                    self.discovered['socket_messages'].append({
                        'message': msg,
                        'time': datetime.now().isoformat()
                    })
                    
        except Exception as e:
            print(f"WebSocket closed: {str(e)}")
            
    async def try_connection(self, url: str, context: Browser):
        """Try to connect to a potential source"""
        try:
            page = await context.new_page()
            self.connections['active'].add(url)
            
            # Try different connection methods
            try:
                # Try WebSocket
                ws = await page.wait_for_websocket(url, timeout=5000)
                self.discovered['websockets'].add(url)
                return ws
            except:
                pass
                
            try:
                # Try regular HTTP
                response = await page.goto(url)
                if response.ok:
                    self.connections['successful'].add(url)
                    return page
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"Connection attempt failed: {url} - {str(e)}")
            
        finally:
            self.connections['active'].remove(url)
            
    async def analyze_connection(self, connection, url: str):
        """Analyze what we found"""
        try:
            if isinstance(connection, WebSocket):
                # Listen for a bit
                start = datetime.utcnow()
                messages = []
                
                while (datetime.utcnow() - start).seconds < 10:
                    try:
                        msg = await connection.receive_text()
                        messages.append(msg)
                        
                        # Look for data patterns
                        if any(x in msg for x in ['source', 'origin', 'master']):
                            self.logger.info(f"Found upstream source: {url}")
                            self.connections['upstream'].add(url)
                            return True
                            
                    except:
                        continue
                        
            elif isinstance(connection, Page):
                # Check page content
                content = await connection.content()
                if any(x in content for x in ['source', 'origin', 'master']):
                    self.logger.info(f"Found interesting page: {url}")
                    self.connections['upstream'].add(url)
                    return True
                    
        except Exception as e:
            self.logger.error(f"Analysis error: {url} - {str(e)}")
            
        return False
        
    async def explore_supplier(self, url: str, context: Browser):
        """Deep dive into a potential supplier"""
        try:
            connection = await self.try_connection(url, context)
            if connection:
                if await self.analyze_connection(connection, url):
                    self.logger.info(f"Found promising supplier: {url}")
                    # Keep this connection alive
                    return connection
                    
        except Exception as e:
            self.logger.error(f"Supplier exploration error: {url} - {str(e)}")
            
    async def random_delay(self):
        """Add random delay between requests"""
        delay = random.uniform(0.5, 2.0)
        await asyncio.sleep(delay)

    async def run(self, base_url: str):
        """Run with advanced browser handling"""
        print("Starting scraper with anti-detection...")
        
        while True:
            try:
                # Setup browser with random configuration
                if not await self.setup_browser():
                    print("Browser setup failed, trying again...")
                    await asyncio.sleep(random.uniform(5, 10))
                    continue
                    
                print(f"Navigating to {base_url}")
                self.driver.get(base_url)
                
                # Wait for page load
                await asyncio.sleep(random.uniform(3, 5))
                
                # Start monitoring network
                await self.monitor_network()
                
                # Run for 10 minutes
                timeout = 600
                start_time = datetime.now()
                
                while (datetime.now() - start_time).seconds < timeout:
                    await asyncio.sleep(1)
                    if (datetime.now() - start_time).seconds % 60 == 0:
                        print(f"Running for {(datetime.now() - start_time).seconds // 60} minutes")
                        print(f"Found {len(self.discovered['websockets'])} WebSocket connections")
                        print(f"Found {len(self.discovered['xhr_requests'])} XHR requests")
                
            except Exception as e:
                print(f"Error: {str(e)}")
                
            finally:
                if hasattr(self, 'driver'):
                    self.driver.quit()
                    
            # Wait before next attempt
            await asyncio.sleep(random.uniform(10, 20))
            
    async def explore_network(self, page: Page):
        """Explore the network to find interesting endpoints"""
        try:
            # Track all network requests
            async def handle_request(route: Route):
                url = route.request.url
                if url:
                    parsed = urlparse(url)
                    self.discovered['endpoints'].add(parsed.netloc)
                    
                    # Look for interesting paths and domains
                    interesting_patterns = [
                        '/api/', '/ws/', '/stream/', '/feed/', '/socket/', 
                        'evolution', 'evo', 'live', 'casino', 'game',
                        'roulette', 'blackjack', 'baccarat'
                    ]
                    
                    if any(pattern in parsed.path.lower() or pattern in parsed.netloc.lower() 
                          for pattern in interesting_patterns):
                        print(f"Found interesting endpoint: {url}")  # Debug log
                        self.discovered['suppliers'].add(url)
                        
                    # Check query parameters
                    params = parse_qs(parsed.query)
                    interesting_params = ['source', 'origin', 'provider', 'game', 'table', 'session']
                    if any(param in params for param in interesting_params):
                        print(f"Found potential source: {url}")  # Debug log
                        self.discovered['origins'].add(url)
                
                # Check headers for WebSocket upgrade
                headers = route.request.headers
                if headers.get('upgrade', '').lower() == 'websocket':
                    print(f"Found WebSocket connection: {url}")  # Debug log
                    self.discovered['websockets'].add(url)
                        
                await route.continue_()
                
            await page.route("**/*", handle_request)
            
        except Exception as e:
            print(f"Network exploration error: {str(e)}")  # Debug log
            self.logger.error(f"Network exploration error: {str(e)}")
            
    async def extract_data(self, page: Page) -> Dict:
        """Required method from BaseScraper - we'll just pass for now since we're exploring"""
        return {
            'discovered': self.discovered,
            'connections': self.connections
        }
