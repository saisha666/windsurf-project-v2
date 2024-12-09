import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import os
from dotenv import load_dotenv
import schedule
import time
from typing import List, Dict

class WebScraper:
    def __init__(self, url: str, log_file: str):
        """
        Initialize the web scraper with logging and configuration
        
        Args:
            url (str): Target website URL
            log_file (str): Path to log file
        """
        load_dotenv()
        
        # Logging configuration
        logging.basicConfig(
            filename=log_file, 
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        
        self.url = url
        self.data_history: List[Dict] = []
    
    def fetch_data(self) -> List[Dict]:
        """
        Fetch and parse data from the target website
        
        Returns:
            List[Dict]: Extracted data
        """
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Example: Scraping Hacker News titles and links
            items = soup.find_all('a', class_='titlelink')
            
            scraped_data = [
                {
                    'title': item.text,
                    'link': item.get('href'),
                    'timestamp': pd.Timestamp.now()
                } 
                for item in items
            ]
            
            logging.info(f"Scraped {len(scraped_data)} items")
            return scraped_data
        
        except requests.RequestException as e:
            logging.error(f"Scraping error: {e}")
            return []
    
    def save_data(self, data: List[Dict], format: str = 'csv'):
        """
        Save scraped data to a file
        
        Args:
            data (List[Dict]): Data to save
            format (str): Output file format
        """
        if not data:
            logging.warning("No data to save")
            return
        
        df = pd.DataFrame(data)
        
        if format == 'csv':
            df.to_csv('scraped_data.csv', index=False, mode='a', header=not os.path.exists('scraped_data.csv'))
        elif format == 'json':
            df.to_json('scraped_data.json', orient='records', mode='a')
        
        logging.info(f"Data saved in {format} format")
    
    def run(self):
        """
        Main scraping method that runs periodically
        """
        data = self.fetch_data()
        if data:
            self.save_data(data, os.getenv('OUTPUT_FORMAT', 'csv'))

def main():
    # Load configuration from .env
    load_dotenv()
    
    target_url = os.getenv('TARGET_URL', 'https://news.ycombinator.com/')
    interval = int(os.getenv('SCRAPE_INTERVAL', 5))
    log_file = os.getenv('LOG_FILE', 'scraper.log')
    
    scraper = WebScraper(target_url, log_file)
    
    # Schedule the scraping job
    schedule.every(interval).minutes.do(scraper.run)
    
    logging.info(f"Scraper started. Targeting {target_url}, interval: {interval} minutes")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
