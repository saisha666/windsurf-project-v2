import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

class DataPreprocessor:
    def __init__(self):
        self.load_config()
        
    def load_config(self):
        """Load configuration settings"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'storage.json')
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
    def load_data(self):
        """Load and combine data from all sources"""
        data_dir = os.path.join(self.config['data_root'], 'System', 'Cache')
        all_data = []
        
        for file in os.listdir(data_dir):
            if file.endswith('.json'):
                with open(os.path.join(data_dir, file), 'r') as f:
                    data = json.load(f)
                    all_data.extend(data)
                    
        return pd.DataFrame(all_data)
        
    def extract_time_features(self, df):
        """Extract time-based features"""
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        # Calculate time differences
        df['time_diff'] = df['timestamp'].diff().dt.total_seconds()
        df['spin_duration'] = df['time_diff'].fillna(0)
        
        return df
        
    def extract_sequence_features(self, df):
        """Extract sequence-based features"""
        # Previous numbers
        for i in range(1, 6):
            df[f'prev_{i}'] = df['number'].shift(i)
            
        # Count consecutive same numbers
        df['consecutive_same'] = (df['number'] == df['number'].shift(1)).astype(int)
        for i in range(2, 6):
            df['consecutive_same'] += (df['number'] == df['number'].shift(i)).astype(int)
            
        # Time since last occurrence of each number
        for num in range(37):
            mask = df['number'] == num
            df[f'last_seen_{num}'] = mask.cumsum()
            df[f'time_since_{num}'] = df.groupby(f'last_seen_{num}').cumcount()
            
        df['time_since_last'] = df.apply(
            lambda row: row[f'time_since_{int(row["number"])}'], axis=1
        )
        
        # Clean up temporary columns
        for num in range(37):
            df = df.drop([f'last_seen_{num}', f'time_since_{num}'], axis=1)
            
        return df
        
    def extract_pattern_features(self, df):
        """Extract pattern-based features"""
        # Number properties
        df['is_red'] = df['number'].isin([1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36])
        df['is_black'] = df['number'].isin([2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35])
        df['is_zero'] = df['number'] == 0
        
        # Sector features
        df['sector'] = pd.cut(df['number'], 
                            bins=[-1,12,24,36], 
                            labels=['first_12','second_12','third_12'])
                            
        # Column features
        first_col = [1,4,7,10,13,16,19,22,25,28,31,34]
        second_col = [2,5,8,11,14,17,20,23,26,29,32,35]
        df['column'] = df['number'].apply(
            lambda x: 'first' if x in first_col else 
                     'second' if x in second_col else 
                     'third' if x not in [0] else 'zero'
        )
        
        # Hot/Cold numbers
        window = 100
        number_counts = pd.get_dummies(df['number']).rolling(window=window).sum()
        df['number_frequency'] = number_counts.lookup(
            number_counts.index, df['number'].astype(str)
        )
        df['is_hot'] = df['number_frequency'] > number_counts.mean(axis=1)
        df['is_cold'] = df['number_frequency'] < number_counts.mean(axis=1)
        
        return df
        
    def preprocess_data(self):
        """Main preprocessing function"""
        # Load data
        df = self.load_data()
        
        # Extract features
        df = self.extract_time_features(df)
        df = self.extract_sequence_features(df)
        df = self.extract_pattern_features(df)
        
        # Handle missing values
        df = df.fillna(0)
        
        # Convert categorical variables
        categorical_columns = ['sector', 'column']
        df = pd.get_dummies(df, columns=categorical_columns)
        
        return df
        
    def prepare_recent_data(self, recent_numbers):
        """Prepare recent numbers for prediction"""
        current_time = datetime.now()
        
        # Create a small dataframe with recent numbers
        data = []
        for i, num in enumerate(recent_numbers):
            data.append({
                'number': num,
                'timestamp': current_time - pd.Timedelta(seconds=30*(len(recent_numbers)-i)),
                'provider_id': 1,  # Assuming single provider for now
                'table_id': 1      # Assuming single table for now
            })
            
        df = pd.DataFrame(data)
        
        # Apply same preprocessing steps
        df = self.extract_time_features(df)
        df = self.extract_sequence_features(df)
        df = self.extract_pattern_features(df)
        
        # Handle missing values
        df = df.fillna(0)
        
        # Convert categorical variables
        categorical_columns = ['sector', 'column']
        df = pd.get_dummies(df, columns=categorical_columns)
        
        return df.iloc[-1:] # Return only the last row for prediction
