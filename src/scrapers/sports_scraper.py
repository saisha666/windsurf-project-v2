import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import os
from dotenv import load_dotenv
import schedule
import time
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import plotly.graph_objects as go
import json
from datetime import datetime

class SportsScraper:
    def __init__(self, url: str, log_file: str):
        """Initialize the sports scraper with logging and Selenium setup"""
        load_dotenv()
        
        # Logging configuration
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        
        self.url = url
        self.data_history: List[Dict] = []
        
        # Setup Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        logging.info("SportsScraper initialized successfully")

    def fetch_live_scores(self) -> List[Dict]:
        """Fetch live sports scores from the website"""
        try:
            self.driver.get(self.url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sportScore"))
            )
            
            # Example: Scraping ESPN-style scores (modify selectors based on target website)
            games = self.driver.find_elements(By.CLASS_NAME, "sportScore")
            
            scores_data = []
            for game in games:
                try:
                    score_data = {
                        'timestamp': datetime.now().isoformat(),
                        'home_team': game.find_element(By.CLASS_NAME, "homeTeam").text,
                        'away_team': game.find_element(By.CLASS_NAME, "awayTeam").text,
                        'home_score': game.find_element(By.CLASS_NAME, "homeScore").text,
                        'away_score': game.find_element(By.CLASS_NAME, "awayScore").text,
                        'status': game.find_element(By.CLASS_NAME, "gameStatus").text
                    }
                    scores_data.append(score_data)
                except Exception as e:
                    logging.warning(f"Error parsing individual game: {e}")
                    continue
            
            logging.info(f"Scraped {len(scores_data)} live games")
            return scores_data
            
        except Exception as e:
            logging.error(f"Error fetching live scores: {e}")
            return []

    def analyze_data(self, data: List[Dict]) -> Dict:
        """Analyze the scraped sports data"""
        if not data:
            return {}
        
        df = pd.DataFrame(data)
        
        # Convert scores to numeric
        df['home_score'] = pd.to_numeric(df['home_score'], errors='coerce')
        df['away_score'] = pd.to_numeric(df['away_score'], errors='coerce')
        
        analysis = {
            'total_games': len(df),
            'average_total_score': (df['home_score'] + df['away_score']).mean(),
            'home_win_percentage': (df['home_score'] > df['away_score']).mean() * 100,
            'highest_scoring_game': {
                'home_team': df.loc[df['home_score'] + df['away_score'].idxmax(), 'home_team'],
                'away_team': df.loc[df['home_score'] + df['away_score'].idxmax(), 'away_team'],
                'total_score': df['home_score'].max() + df['away_score'].max()
            }
        }
        
        return analysis

    def create_visualization(self, data: List[Dict], output_file: str = 'score_trends.html'):
        """Create interactive visualizations of the sports data"""
        df = pd.DataFrame(data)
        
        # Create score distribution plot
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['home_team'],
            y=df['home_score'],
            name='Home Scores',
            marker_color='blue'
        ))
        
        fig.add_trace(go.Bar(
            x=df['away_team'],
            y=df['away_score'],
            name='Away Scores',
            marker_color='red'
        ))
        
        fig.update_layout(
            title='Live Game Scores Distribution',
            xaxis_title='Teams',
            yaxis_title='Scores',
            barmode='group'
        )
        
        fig.write_html(output_file)
        logging.info(f"Created visualization: {output_file}")

    def save_data(self, data: List[Dict], format: str = 'csv'):
        """Save scraped sports data to a file"""
        if not data:
            logging.warning("No data to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'csv':
            filename = f'sports_data_{timestamp}.csv'
            pd.DataFrame(data).to_csv(filename, index=False)
        elif format == 'json':
            filename = f'sports_data_{timestamp}.json'
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
        
        logging.info(f"Data saved to {filename}")

    def run(self):
        """Main scraping method that runs periodically"""
        data = self.fetch_live_scores()
        if data:
            self.save_data(data, os.getenv('OUTPUT_FORMAT', 'csv'))
            analysis = self.analyze_data(data)
            logging.info(f"Analysis results: {analysis}")
            self.create_visualization(data)

    def cleanup(self):
        """Clean up resources"""
        self.driver.quit()
        logging.info("Scraper resources cleaned up")

def main():
    # Load configuration from .env
    load_dotenv()
    
    target_url = os.getenv('TARGET_URL', 'https://www.espn.com/live')
    interval = int(os.getenv('SCRAPE_INTERVAL', 1))  # Default to 1 minute for live scores
    log_file = os.getenv('LOG_FILE', 'sports_scraper.log')
    
    scraper = SportsScraper(target_url, log_file)
    
    try:
        # Schedule the scraping job
        schedule.every(interval).minutes.do(scraper.run)
        
        logging.info(f"Sports scraper started. Targeting {target_url}, interval: {interval} minutes")
        
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        logging.info("Scraper stopped by user")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
