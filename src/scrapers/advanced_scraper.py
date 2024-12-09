from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import browsercookie
import json
import os
import time
from datetime import datetime
from ..database.database import DatabaseManager

class AdvancedScraper:
    def __init__(self):
        self.db = DatabaseManager()
        self.setup_browser()
        
    def setup_browser(self):
        """Setup Chrome browser with custom options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Load cookies from browsers
        cookies = browsercookie.load()
        self.cookies = {c.name: c.value for c in cookies}
        
        self.driver = webdriver.Chrome(options=options)
        
    def scrape_url(self, url, wait_time=10):
        """Scrape a URL with advanced waiting and parsing"""
        try:
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page title
            title = self.driver.title
            
            # Get page content
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract useful content
            content = {
                'text': soup.get_text(),
                'links': [{'href': a.get('href'), 'text': a.text} 
                         for a in soup.find_all('a', href=True)],
                'images': [{'src': img.get('src'), 'alt': img.get('alt')} 
                          for img in soup.find_all('img')],
                'tables': [self._parse_table(table) 
                          for table in soup.find_all('table')],
                'metadata': {
                    'scrape_time': datetime.utcnow().isoformat(),
                    'url': url,
                }
            }
            
            # Save to database
            self.db.save_website_data(url, title, content)
            
            return content
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
            
    def _parse_table(self, table):
        """Parse HTML table into structured data"""
        rows = []
        for tr in table.find_all('tr'):
            row = []
            for td in tr.find_all(['td', 'th']):
                row.append(td.get_text().strip())
            if row:
                rows.append(row)
        return rows
    
    def monitor_browser_activity(self):
        """Monitor and record browser activity"""
        try:
            # Get browser history
            history = self.driver.execute_script("""
                return window.performance.getEntriesByType('navigation')
                    .map(entry => ({
                        url: entry.name,
                        timing: {
                            loadTime: entry.loadEventEnd - entry.loadEventStart,
                            domContentLoaded: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
                            firstPaint: entry.responseEnd - entry.requestStart
                        }
                    }));
            """)
            
            # Save to database
            for entry in history:
                self.db.save_browser_history(
                    url=entry['url'],
                    title=self.driver.title,
                    metadata={'timing': entry['timing']}
                )
                
        except Exception as e:
            print(f"Error monitoring browser: {str(e)}")
    
    def analyze_page_structure(self, url):
        """Analyze page structure for better scraping"""
        try:
            self.driver.get(url)
            
            # Analyze DOM structure
            structure = self.driver.execute_script("""
                function analyzeElement(element, depth = 0) {
                    return {
                        tag: element.tagName.toLowerCase(),
                        id: element.id,
                        classes: Array.from(element.classList),
                        children: Array.from(element.children).map(
                            child => analyzeElement(child, depth + 1)
                        ),
                        depth: depth
                    }
                }
                return analyzeElement(document.body);
            """)
            
            return structure
            
        except Exception as e:
            print(f"Error analyzing page structure: {str(e)}")
            return None
    
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()
