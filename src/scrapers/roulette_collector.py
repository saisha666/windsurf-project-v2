from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pandas as pd
import numpy as np
import json
import time
from ..database.database import DatabaseManager

class RouletteDataCollector:
    def __init__(self):
        self.db = DatabaseManager()
        self.setup_browser()
        self.patterns = {
            'consecutive_numbers': [],
            'hot_numbers': {},
            'cold_numbers': {},
            'sector_hits': {},
            'color_sequences': []
        }
        
    def setup_browser(self):
        """Setup Chrome browser with custom options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Add custom preferences for faster loading
        prefs = {
            'profile.managed_default_content_settings.images': 2,  # Disable images
            'disk-cache-size': 4096  # 4GB cache
        }
        options.add_experimental_option('prefs', prefs)
        
        self.driver = webdriver.Chrome(options=options)
        
    def collect_live_data(self, url, duration_minutes=60):
        """Collect live roulette data for specified duration"""
        try:
            self.driver.get(url)
            start_time = datetime.now()
            numbers = []
            timestamps = []
            
            while (datetime.now() - start_time).total_seconds() < duration_minutes * 60:
                try:
                    # Wait for new number
                    number_element = WebDriverWait(self.driver, 60).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "number"))
                    )
                    
                    number = int(number_element.text)
                    timestamp = datetime.now()
                    
                    numbers.append(number)
                    timestamps.append(timestamp)
                    
                    # Analyze patterns in real-time
                    self._update_patterns(numbers)
                    
                    # Save to database
                    self._save_spin(number, timestamp)
                    
                except Exception as e:
                    print(f"Error collecting number: {str(e)}")
                    continue
                    
            return pd.DataFrame({
                'number': numbers,
                'timestamp': timestamps,
                'patterns': [self.patterns.copy() for _ in numbers]
            })
            
        except Exception as e:
            print(f"Error in data collection: {str(e)}")
            return None
            
    def _update_patterns(self, numbers):
        """Update pattern analysis with new number"""
        if len(numbers) < 2:
            return
            
        latest = numbers[-1]
        
        # Update hot and cold numbers
        for num in range(37):
            count = numbers.count(num)
            if count > len(numbers) / 37:  # More frequent than average
                self.patterns['hot_numbers'][num] = count
            elif count < len(numbers) / 37:  # Less frequent than average
                self.patterns['cold_numbers'][num] = count
                
        # Update consecutive patterns
        if len(numbers) >= 5:
            self.patterns['consecutive_numbers'] = numbers[-5:]
            
        # Update sector hits
        sectors = {
            'first_12': range(1, 13),
            'second_12': range(13, 25),
            'third_12': range(25, 37),
            'zero': [0]
        }
        
        for sector_name, sector_range in sectors.items():
            if latest in sector_range:
                self.patterns['sector_hits'][sector_name] = \
                    self.patterns['sector_hits'].get(sector_name, 0) + 1
                    
        # Update color sequences
        colors = []
        for num in numbers[-10:]:  # Last 10 numbers
            if num == 0:
                colors.append('green')
            elif num in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]:
                colors.append('red')
            else:
                colors.append('black')
        self.patterns['color_sequences'] = colors
        
    def _save_spin(self, number, timestamp):
        """Save spin data to database"""
        data = {
            'number': number,
            'timestamp': timestamp.isoformat(),
            'patterns': self.patterns
        }
        
        self.db.save_website_data(
            url='roulette_spins',
            title=f'Spin {timestamp}',
            content=data
        )
        
    def analyze_historical_data(self, start_date=None):
        """Analyze historical roulette data"""
        try:
            # Get historical data from database
            data = self.db.get_website_data(url='roulette_spins')
            if not data:
                return None
                
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    'number': d.content['number'],
                    'timestamp': pd.to_datetime(d.content['timestamp']),
                    'patterns': d.content['patterns']
                }
                for d in data
            ])
            
            if start_date:
                df = df[df['timestamp'] >= pd.to_datetime(start_date)]
                
            # Calculate statistics
            stats = {
                'total_spins': len(df),
                'number_frequency': df['number'].value_counts().to_dict(),
                'hourly_distribution': df.groupby(df['timestamp'].dt.hour)['number'].count().to_dict(),
                'patterns': self._analyze_patterns(df['number'].tolist())
            }
            
            return stats
            
        except Exception as e:
            print(f"Error analyzing historical data: {str(e)}")
            return None
            
    def _analyze_patterns(self, numbers):
        """Analyze patterns in number sequence"""
        patterns = {
            'repeating_sequences': [],
            'number_gaps': {},
            'sector_trends': {},
            'statistical_metrics': {}
        }
        
        # Find repeating sequences
        for length in range(2, 6):
            sequences = [
                tuple(numbers[i:i+length])
                for i in range(len(numbers)-length+1)
            ]
            for seq in set(sequences):
                count = sequences.count(seq)
                if count > 1:
                    patterns['repeating_sequences'].append({
                        'sequence': seq,
                        'count': count
                    })
                    
        # Calculate number gaps
        for num in range(37):
            indices = [i for i, n in enumerate(numbers) if n == num]
            if indices:
                gaps = [indices[i+1] - indices[i] for i in range(len(indices)-1)]
                patterns['number_gaps'][num] = {
                    'avg_gap': np.mean(gaps) if gaps else 0,
                    'max_gap': max(gaps) if gaps else 0
                }
                
        # Analyze sector trends
        sectors = {
            'first_12': range(1, 13),
            'second_12': range(13, 25),
            'third_12': range(25, 37),
            'zero': [0]
        }
        
        for sector_name, sector_range in sectors.items():
            sector_hits = [n for n in numbers if n in sector_range]
            patterns['sector_trends'][sector_name] = {
                'hits': len(sector_hits),
                'percentage': len(sector_hits) / len(numbers) * 100
            }
            
        # Calculate statistical metrics
        patterns['statistical_metrics'] = {
            'mean': np.mean(numbers),
            'std': np.std(numbers),
            'median': np.median(numbers),
            'mode': pd.Series(numbers).mode().tolist()
        }
        
        return patterns
        
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()
