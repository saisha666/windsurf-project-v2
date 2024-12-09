import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
import logging

class TimeAnalyzer:
    """Analyzes time-based patterns and trends in roulette data"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.analysis_cache = {}
        self.time_windows = {
            "1h": timedelta(hours=1),
            "4h": timedelta(hours=4),
            "12h": timedelta(hours=12),
            "1d": timedelta(days=1),
            "1w": timedelta(days=7),
            "1m": timedelta(days=30)
        }
    
    def analyze_time_patterns(self, data: pd.DataFrame, 
                            time_window: str = "1d") -> Dict:
        """Analyze patterns within a specific time window"""
        try:
            if time_window not in self.time_windows:
                raise ValueError(f"Invalid time window: {time_window}")
                
            window = self.time_windows[time_window]
            now = datetime.now()
            
            # Filter data for time window
            mask = (data['timestamp'] >= (now - window))
            window_data = data[mask].copy()
            
            if window_data.empty:
                return {}
            
            # Analyze patterns
            patterns = {
                "number_frequency": window_data['number'].value_counts().to_dict(),
                "color_distribution": window_data['color'].value_counts().to_dict(),
                "sector_trends": self._analyze_sectors(window_data),
                "sequence_patterns": self._find_sequences(window_data['number'].tolist()),
                "time_of_day": self._analyze_time_of_day(window_data),
                "win_streaks": self._analyze_streaks(window_data)
            }
            
            # Cache analysis
            cache_key = f"{time_window}_{now.strftime('%Y%m%d_%H')}"
            self.analysis_cache[cache_key] = {
                "patterns": patterns,
                "timestamp": now.isoformat(),
                "sample_size": len(window_data)
            }
            
            return patterns
            
        except Exception as e:
            logging.error(f"Error analyzing time patterns: {str(e)}")
            return {}
    
    def _analyze_sectors(self, data: pd.DataFrame) -> Dict:
        """Analyze sector-based patterns"""
        sectors = {
            "low": (data['number'] <= 18).sum(),
            "high": (data['number'] > 18).sum(),
            "first12": ((data['number'] >= 1) & (data['number'] <= 12)).sum(),
            "second12": ((data['number'] >= 13) & (data['number'] <= 24)).sum(),
            "third12": ((data['number'] >= 25) & (data['number'] <= 36)).sum(),
            "zero": (data['number'] == 0).sum()
        }
        
        total = len(data)
        return {k: v/total for k, v in sectors.items()} if total > 0 else {}
    
    def _find_sequences(self, numbers: List[int], min_length: int = 3) -> List[Dict]:
        """Find recurring number sequences"""
        sequences = []
        n = len(numbers)
        
        for i in range(n - min_length + 1):
            seq = numbers[i:i + min_length]
            # Look for this sequence in the rest of the numbers
            count = 0
            for j in range(i + 1, n - min_length + 1):
                if numbers[j:j + min_length] == seq:
                    count += 1
            if count > 0:
                sequences.append({
                    "sequence": seq,
                    "occurrences": count + 1,
                    "last_seen": i
                })
        
        return sorted(sequences, key=lambda x: x['occurrences'], reverse=True)[:5]
    
    def _analyze_time_of_day(self, data: pd.DataFrame) -> Dict:
        """Analyze patterns based on time of day"""
        data['hour'] = pd.to_datetime(data['timestamp']).dt.hour
        hourly_stats = {}
        
        for hour in range(24):
            hour_data = data[data['hour'] == hour]
            if not hour_data.empty:
                hourly_stats[str(hour)] = {
                    "spins": len(hour_data),
                    "most_common": hour_data['number'].mode().iloc[0],
                    "hot_numbers": hour_data['number'].value_counts().nlargest(3).to_dict()
                }
        
        return hourly_stats
    
    def _analyze_streaks(self, data: pd.DataFrame) -> Dict:
        """Analyze winning and pattern streaks"""
        streaks = {
            "color": self._find_color_streaks(data),
            "sector": self._find_sector_streaks(data),
            "even_odd": self._find_even_odd_streaks(data)
        }
        return streaks
    
    def _find_color_streaks(self, data: pd.DataFrame) -> Dict:
        """Find streaks of same color"""
        colors = data['color'].tolist()
        return self._calculate_streaks(colors)
    
    def _find_sector_streaks(self, data: pd.DataFrame) -> Dict:
        """Find streaks in sectors"""
        sectors = ['low' if n <= 18 else 'high' for n in data['number']]
        return self._calculate_streaks(sectors)
    
    def _find_even_odd_streaks(self, data: pd.DataFrame) -> Dict:
        """Find streaks of even/odd numbers"""
        even_odd = ['even' if n % 2 == 0 else 'odd' for n in data['number']]
        return self._calculate_streaks(even_odd)
    
    def _calculate_streaks(self, sequence: List) -> Dict:
        """Calculate streak statistics"""
        current_streak = 1
        max_streak = 1
        current_value = sequence[0]
        streaks = []
        
        for i in range(1, len(sequence)):
            if sequence[i] == sequence[i-1]:
                current_streak += 1
            else:
                streaks.append({
                    "value": current_value,
                    "length": current_streak
                })
                current_streak = 1
                current_value = sequence[i]
            max_streak = max(max_streak, current_streak)
        
        streaks.append({
            "value": current_value,
            "length": current_streak
        })
        
        return {
            "max_streak": max_streak,
            "recent_streaks": sorted(streaks, key=lambda x: x['length'], reverse=True)[:5]
        }
    
    def get_trend_analysis(self, time_windows: List[str] = None) -> Dict:
        """Get trend analysis across multiple time windows"""
        if time_windows is None:
            time_windows = list(self.time_windows.keys())
            
        trends = {}
        for window in time_windows:
            cache_key = f"{window}_{datetime.now().strftime('%Y%m%d_%H')}"
            if cache_key in self.analysis_cache:
                trends[window] = self.analysis_cache[cache_key]
            
        return trends
    
    def save_analysis(self, analysis: Dict, name: str):
        """Save analysis results to file"""
        try:
            analysis_dir = self.base_path / "analysis"
            analysis_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            with open(analysis_dir / filename, 'w') as f:
                json.dump(analysis, f, indent=4)
                
        except Exception as e:
            logging.error(f"Error saving analysis: {str(e)}")
    
    def load_analysis(self, name: str, time_range: Optional[Tuple[datetime, datetime]] = None) -> List[Dict]:
        """Load historical analysis results"""
        try:
            analysis_dir = self.base_path / "analysis"
            if not analysis_dir.exists():
                return []
                
            results = []
            for file in analysis_dir.glob(f"{name}_*.json"):
                # Extract timestamp from filename
                timestamp_str = file.stem.split('_')[-2:]
                timestamp = datetime.strptime('_'.join(timestamp_str), '%Y%m%d_%H%M')
                
                if time_range:
                    start, end = time_range
                    if not (start <= timestamp <= end):
                        continue
                
                with open(file, 'r') as f:
                    analysis = json.load(f)
                    analysis['timestamp'] = timestamp.isoformat()
                    results.append(analysis)
            
            return sorted(results, key=lambda x: x['timestamp'])
            
        except Exception as e:
            logging.error(f"Error loading analysis: {str(e)}")
            return []
