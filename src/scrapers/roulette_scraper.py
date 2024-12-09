import time
from datetime import datetime
import sqlite3
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import json
import os
import random
import undetected_chromedriver as uc
from fake_useragent import UserAgent

class RouletteScraper:
    def __init__(self, db_path='data.sqlite'):
        """Initialize the roulette scraper with stealth features"""
        self.db_path = os.path.join(os.path.expanduser('~'), 'Documents', db_path)
        self.setup_database()
        
        # Initialize undetected Chrome with stealth settings
        options = uc.ChromeOptions()
        ua = UserAgent()
        options.add_argument(f'--user-agent={ua.random}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        
        # Random window size to avoid detection
        widths = [1280, 1366, 1440, 1600, 1920]
        heights = [768, 900, 1024, 1200]
        width = random.choice(widths)
        height = random.choice(heights)
        options.add_argument(f'--window-size={width},{height}')
        
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, random.uniform(8, 12))
        
        # Add random delays between actions
        self.min_delay = 1.0
        self.max_delay = 3.0
        
        print("\n=== Data Collector ===")
        print("Controls:")
        print("- Press 'q' to quit")
        print("- Press 's' to save")
        print("- Press 'v' to view")
        print("=" * 20 + "\n")
    
    def random_delay(self):
        """Add random delay between actions"""
        time.sleep(random.uniform(self.min_delay, self.max_delay))
    
    def setup_database(self):
        """Create encrypted SQLite database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME,
            val INTEGER,
            cat1 TEXT,
            cat2 TEXT,
            cat3 TEXT,
            cat4 TEXT,
            cat5 TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts DATETIME,
            type TEXT,
            data TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def categorize_number(self, number):
        """Categorize a roulette number"""
        number = int(number)
        
        # Color
        red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        color = 'red' if number in red_numbers else 'black' if number > 0 else 'green'
        
        # Odd/Even
        odd_even = 'odd' if number % 2 else 'even' if number > 0 else 'zero'
        
        # Dozen
        if number == 0:
            dozen = 'zero'
        elif 1 <= number <= 12:
            dozen = 'first'
        elif 13 <= number <= 24:
            dozen = 'second'
        else:
            dozen = 'third'
        
        # Column
        if number == 0:
            column = 'zero'
        elif number % 3 == 1:
            column = 'first'
        elif number % 3 == 2:
            column = 'second'
        else:
            column = 'third'
        
        # High/Low
        high_low = 'high' if number > 18 else 'low' if number > 0 else 'zero'
        
        return {
            'number': number,
            'color': color,
            'odd_even': odd_even,
            'dozen': dozen,
            'column': column,
            'high_low': high_low
        }
    
    def save_round(self, number):
        """Save data point with obfuscated column names"""
        categories = self.categorize_number(number)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO data (ts, val, cat1, cat2, cat3, cat4, cat5)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            categories['number'],
            categories['color'],
            categories['odd_even'],
            categories['dozen'],
            categories['column'],
            categories['high_low']
        ))
        
        conn.commit()
        conn.close()
        self.random_delay()
    
    def calculate_statistics(self):
        """Calculate various statistics from the rounds"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM data", conn)
        
        stats = {}
        
        # Last 10 numbers
        stats['last_10'] = df['val'].tail(10).tolist()
        
        # Most common numbers
        stats['most_common_numbers'] = df['val'].value_counts().head(5).to_dict()
        
        # Color distribution
        stats['color_distribution'] = df['cat1'].value_counts().to_dict()
        
        # Odd/Even distribution
        stats['odd_even_distribution'] = df['cat2'].value_counts().to_dict()
        
        # Dozen distribution
        stats['dozen_distribution'] = df['cat3'].value_counts().to_dict()
        
        # Column distribution
        stats['column_distribution'] = df['cat4'].value_counts().to_dict()
        
        # High/Low distribution
        stats['high_low_distribution'] = df['cat5'].value_counts().to_dict()
        
        # Pattern analysis
        if len(df) >= 10:
            # Analyze last 10 rounds for patterns
            last_10 = df['val'].tail(10).tolist()
            
            # Check for number repetition
            repeats = [num for num in last_10 if last_10.count(num) > 1]
            stats['repeating_numbers'] = list(set(repeats))
            
            # Check for color patterns
            last_10_colors = df['cat1'].tail(10).tolist()
            color_streaks = self.find_streaks(last_10_colors)
            stats['color_streaks'] = color_streaks
            
            # Check for odd/even patterns
            last_10_odd_even = df['cat2'].tail(10).tolist()
            odd_even_streaks = self.find_streaks(last_10_odd_even)
            stats['odd_even_streaks'] = odd_even_streaks
            
            # Check for dozen patterns
            last_10_dozens = df['cat3'].tail(10).tolist()
            dozen_streaks = self.find_streaks(last_10_dozens)
            stats['dozen_streaks'] = dozen_streaks
            
            # Predict next numbers
            stats['predictions'] = self.predict_next(df)
        
        # Save statistics
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO analysis (ts, type, data)
        VALUES (?, ?, ?)
        ''', (datetime.now(), 'all_stats', json.dumps(stats)))
        
        conn.commit()
        conn.close()
        
        return stats
    
    def find_streaks(self, values):
        """Find streaks in a sequence of values"""
        streaks = []
        current_streak = [values[0]]
        
        for i in range(1, len(values)):
            if values[i] == values[i-1]:
                current_streak.append(values[i])
            else:
                if len(current_streak) > 1:
                    streaks.append((current_streak[0], len(current_streak)))
                current_streak = [values[i]]
        
        if len(current_streak) > 1:
            streaks.append((current_streak[0], len(current_streak)))
        
        return streaks
    
    def predict_next(self, df):
        """Predict potential next numbers based on patterns"""
        predictions = {
            'hot_numbers': [],
            'cold_numbers': [],
            'due_numbers': [],
            'pattern_based': []
        }
        
        # Get hot numbers (appeared frequently in last 50 spins)
        last_50 = df['val'].tail(50)
        value_counts = last_50.value_counts()
        hot_numbers = value_counts[value_counts >= 2].index.tolist()
        predictions['hot_numbers'] = hot_numbers[:5]  # Top 5 hot numbers
        
        # Get cold numbers (haven't appeared in last 50 spins)
        all_numbers = set(range(37))
        appeared = set(last_50.unique())
        cold_numbers = list(all_numbers - appeared)
        predictions['cold_numbers'] = cold_numbers[:5]  # Top 5 cold numbers
        
        # Get due numbers (haven't appeared in a while)
        last_occurrence = {}
        for i, num in enumerate(reversed(df['val'].tolist())):
            if num not in last_occurrence:
                last_occurrence[num] = i
        
        due_numbers = sorted(last_occurrence.items(), key=lambda x: x[1], reverse=True)
        predictions['due_numbers'] = [num for num, _ in due_numbers[:5]]  # Top 5 due numbers
        
        # Pattern-based predictions
        last_5 = df['val'].tail(5).tolist()
        
        # Check for repeating differences
        diffs = [last_5[i] - last_5[i-1] for i in range(1, len(last_5))]
        if len(set(diffs)) < len(diffs):  # If there are repeating differences
            most_common_diff = max(set(diffs), key=diffs.count)
            next_num = (last_5[-1] + most_common_diff) % 37
            predictions['pattern_based'].append(next_num)
        
        return predictions
    
    def print_statistics(self):
        """Print current statistics and predictions"""
        stats = self.calculate_statistics()
        
        print("\n=== Current Statistics ===")
        print("\nLast 10 numbers:", stats['last_10'])
        
        print("\nMost common numbers:")
        for num, count in stats['most_common_numbers'].items():
            print(f"Number {num}: {count} times")
        
        if 'predictions' in stats:
            print("\n=== Predictions ===")
            print("\nHot numbers (frequent recently):", stats['predictions']['hot_numbers'])
            print("Cold numbers (haven't appeared):", stats['predictions']['cold_numbers'])
            print("Due numbers (overdue):", stats['predictions']['due_numbers'])
            if stats['predictions']['pattern_based']:
                print("Pattern-based predictions:", stats['predictions']['pattern_based'])
        
        if 'repeating_numbers' in stats:
            print("\n=== Patterns Detected ===")
            if stats['repeating_numbers']:
                print("Repeating numbers:", stats['repeating_numbers'])
            
            if stats['color_streaks']:
                print("\nColor streaks:")
                for color, length in stats['color_streaks']:
                    print(f"{color.capitalize()} streak of {length}")
            
            if stats['odd_even_streaks']:
                print("\nOdd/Even streaks:")
                for type_, length in stats['odd_even_streaks']:
                    print(f"{type_.capitalize()} streak of {length}")
            
            if stats['dozen_streaks']:
                print("\nDozen streaks:")
                for dozen, length in stats['dozen_streaks']:
                    print(f"{dozen.capitalize()} dozen streak of {length}")
    
    def run(self):
        """Main loop with stealth features"""
        print("Starting collection...")
        print("Enter values or commands (q/s/v)")
        
        try:
            while True:
                user_input = input("\nValue: ").lower()
                
                if user_input == 'q':
                    break
                elif user_input == 's':
                    self.calculate_statistics()
                    print("Saved!")
                elif user_input == 'v':
                    self.print_statistics()
                else:
                    try:
                        number = int(user_input)
                        if 0 <= number <= 36:
                            self.save_round(number)
                            print("✓")  # Simple checkmark instead of detailed output
                        else:
                            print("!")  # Simple error indicator
                    except ValueError:
                        print("!")
                
                self.random_delay()
        
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.driver.quit()
            self.print_statistics()

def main():
    scraper = RouletteScraper()
    scraper.run()

if __name__ == "__main__":
    main()
