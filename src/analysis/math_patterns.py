import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from datetime import datetime, timedelta

@dataclass
class RouletteNumber:
    number: int
    color: str
    sector: str
    timestamp: datetime
    
    @property
    def is_red(self) -> bool:
        return self.color == 'red'
    
    @property
    def is_black(self) -> bool:
        return self.color == 'black'
    
    @property
    def is_zero(self) -> bool:
        return self.number == 0
    
    @property
    def is_even(self) -> bool:
        return self.number % 2 == 0 and not self.is_zero
    
    @property
    def dozen(self) -> int:
        if self.is_zero:
            return 0
        return ((self.number - 1) // 12) + 1

class MathematicalAnalyzer:
    """Advanced mathematical analysis for roulette patterns"""
    
    def __init__(self):
        self.number_mapping = {
            0: {'color': 'green', 'sector': 'zero'},
            32: {'color': 'red', 'sector': 'third'},
            15: {'color': 'black', 'sector': 'second'},
            19: {'color': 'red', 'sector': 'second'},
            4: {'color': 'black', 'sector': 'first'},
            21: {'color': 'red', 'sector': 'second'},
            2: {'color': 'black', 'sector': 'first'},
            25: {'color': 'red', 'sector': 'third'},
            17: {'color': 'black', 'sector': 'second'},
            34: {'color': 'red', 'sector': 'third'},
            6: {'color': 'black', 'sector': 'first'},
            27: {'color': 'red', 'sector': 'third'},
            13: {'color': 'black', 'sector': 'second'},
            36: {'color': 'red', 'sector': 'third'},
            11: {'color': 'black', 'sector': 'first'},
            30: {'color': 'red', 'sector': 'third'},
            8: {'color': 'black', 'sector': 'first'},
            23: {'color': 'red', 'sector': 'second'},
            10: {'color': 'black', 'sector': 'first'},
            5: {'color': 'red', 'sector': 'first'},
            24: {'color': 'black', 'sector': 'second'},
            16: {'color': 'red', 'sector': 'second'},
            33: {'color': 'black', 'sector': 'third'},
            1: {'color': 'red', 'sector': 'first'},
            20: {'color': 'black', 'sector': 'second'},
            14: {'color': 'red', 'sector': 'second'},
            31: {'color': 'black', 'sector': 'third'},
            9: {'color': 'red', 'sector': 'first'},
            22: {'color': 'black', 'sector': 'second'},
            18: {'color': 'red', 'sector': 'second'},
            29: {'color': 'black', 'sector': 'third'},
            7: {'color': 'red', 'sector': 'first'},
            28: {'color': 'black', 'sector': 'third'},
            12: {'color': 'red', 'sector': 'first'},
            35: {'color': 'black', 'sector': 'third'},
            3: {'color': 'red', 'sector': 'first'},
            26: {'color': 'black', 'sector': 'third'}
        }
        
        # Initialize pattern trackers
        self.sequence_patterns = defaultdict(int)
        self.hot_numbers = defaultdict(int)
        self.cold_numbers = set(range(37))
        self.sector_trends = defaultdict(list)
        self.time_patterns = []
        
    def create_roulette_number(self, number: int, timestamp: datetime) -> RouletteNumber:
        """Create a RouletteNumber object with full metadata"""
        mapping = self.number_mapping[number]
        return RouletteNumber(
            number=number,
            color=mapping['color'],
            sector=mapping['sector'],
            timestamp=timestamp
        )
    
    def analyze_sequence(self, numbers: List[int], window_size: int = 5) -> Dict:
        """Analyze number sequences for patterns"""
        sequences = defaultdict(int)
        for i in range(len(numbers) - window_size + 1):
            seq = tuple(numbers[i:i + window_size])
            sequences[seq] += 1
            
        # Find most common sequences
        common_sequences = sorted(
            sequences.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return {
            'sequences': dict(common_sequences),
            'most_frequent': common_sequences[0] if common_sequences else None
        }
    
    def analyze_sector_distribution(self, numbers: List[RouletteNumber]) -> Dict:
        """Analyze sector distribution and trends"""
        sector_counts = defaultdict(int)
        sector_sequences = []
        
        for num in numbers:
            sector_counts[num.sector] += 1
            sector_sequences.append(num.sector)
        
        # Calculate sector probabilities
        total = len(numbers)
        sector_probs = {
            sector: count/total 
            for sector, count in sector_counts.items()
        }
        
        # Detect sector streaks
        current_streak = {'sector': None, 'count': 0}
        max_streak = {'sector': None, 'count': 0}
        
        for sector in sector_sequences:
            if sector == current_streak['sector']:
                current_streak['count'] += 1
                if current_streak['count'] > max_streak['count']:
                    max_streak = current_streak.copy()
            else:
                current_streak = {'sector': sector, 'count': 1}
        
        return {
            'distributions': sector_probs,
            'max_streak': max_streak,
            'current_trend': self._detect_sector_trend(sector_sequences[-10:])
        }
    
    def _detect_sector_trend(self, recent_sectors: List[str]) -> str:
        """Detect trends in sector sequences"""
        if len(recent_sectors) < 3:
            return "insufficient_data"
            
        sector_values = {'first': 1, 'second': 2, 'third': 3}
        numeric_sectors = [sector_values[s] for s in recent_sectors if s != 'zero']
        
        if len(numeric_sectors) < 3:
            return "zero_dominant"
            
        # Calculate trend using linear regression
        x = np.arange(len(numeric_sectors))
        slope, _, r_value, _, _ = stats.linregress(x, numeric_sectors)
        
        if abs(r_value) < 0.5:
            return "random"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"
    
    def analyze_time_patterns(self, numbers: List[RouletteNumber]) -> Dict:
        """Analyze temporal patterns in number occurrence"""
        time_diffs = []
        number_times = defaultdict(list)
        
        for i in range(1, len(numbers)):
            diff = (numbers[i].timestamp - numbers[i-1].timestamp).total_seconds()
            time_diffs.append(diff)
            number_times[numbers[i].number].append(numbers[i].timestamp)
        
        # Calculate timing statistics
        avg_time = np.mean(time_diffs) if time_diffs else 0
        std_time = np.std(time_diffs) if time_diffs else 0
        
        # Find numbers with regular timing
        regular_numbers = {}
        for num, times in number_times.items():
            if len(times) > 2:
                time_diffs = np.diff([t.timestamp() for t in times])
                regularity = np.std(time_diffs)
                if regularity < std_time:
                    regular_numbers[num] = regularity
        
        return {
            'avg_spin_time': avg_time,
            'time_consistency': std_time,
            'regular_numbers': regular_numbers
        }
    
    def find_hot_cold_numbers(self, 
                            numbers: List[RouletteNumber], 
                            window: int = 100) -> Tuple[List[int], List[int]]:
        """Identify hot and cold numbers"""
        recent_numbers = numbers[-window:] if len(numbers) > window else numbers
        number_freq = defaultdict(int)
        
        for num in recent_numbers:
            number_freq[num.number] += 1
            
        # Calculate expected frequency
        expected_freq = window / 37
        
        # Identify hot and cold numbers
        hot_numbers = []
        cold_numbers = []
        
        for num in range(37):
            freq = number_freq[num]
            if freq > expected_freq * 1.5:
                hot_numbers.append((num, freq))
            elif freq < expected_freq * 0.5:
                cold_numbers.append((num, freq))
                
        return (
            sorted(hot_numbers, key=lambda x: x[1], reverse=True),
            sorted(cold_numbers, key=lambda x: x[1])
        )
    
    def detect_biases(self, numbers: List[RouletteNumber]) -> Dict:
        """Detect potential biases in the wheel"""
        number_counts = defaultdict(int)
        total_spins = len(numbers)
        
        for num in numbers:
            number_counts[num.number] += 1
        
        # Calculate chi-square test for uniformity
        observed = np.array([number_counts[i] for i in range(37)])
        expected = np.full(37, total_spins/37)
        chi2, p_value = stats.chisquare(observed, expected)
        
        # Cluster analysis for potential physical biases
        if total_spins >= 100:
            number_freqs = [number_counts[i]/total_spins for i in range(37)]
            kmeans = KMeans(n_clusters=3, random_state=42)
            clusters = kmeans.fit_predict(np.array(number_freqs).reshape(-1, 1))
            
            bias_groups = defaultdict(list)
            for num in range(37):
                bias_groups[clusters[num]].append(num)
        else:
            bias_groups = {}
        
        return {
            'chi_square_stat': chi2,
            'p_value': p_value,
            'bias_detected': p_value < 0.05,
            'bias_groups': dict(bias_groups)
        }
    
    def predict_patterns(self, 
                        numbers: List[RouletteNumber],
                        confidence_threshold: float = 0.6) -> Dict:
        """Generate pattern-based predictions"""
        if len(numbers) < 20:
            return {'confidence': 0, 'predictions': []}
            
        recent = numbers[-20:]
        
        # Analyze various patterns
        sequence_analysis = self.analyze_sequence([n.number for n in recent])
        sector_analysis = self.analyze_sector_distribution(recent)
        time_analysis = self.analyze_time_patterns(recent)
        hot_cold = self.find_hot_cold_numbers(recent)
        biases = self.detect_biases(recent)
        
        # Generate predictions based on pattern strength
        predictions = []
        confidence_scores = []
        
        # Sequence-based prediction
        if sequence_analysis['most_frequent']:
            seq, freq = sequence_analysis['most_frequent']
            if freq >= 3:
                predictions.append({
                    'type': 'sequence',
                    'numbers': list(seq),
                    'confidence': min(freq/10, 0.8)
                })
                confidence_scores.append(min(freq/10, 0.8))
        
        # Sector trend prediction
        if sector_analysis['current_trend'] in ['increasing', 'decreasing']:
            trend_conf = 0.7 if sector_analysis['current_trend'] == 'increasing' else 0.6
            predictions.append({
                'type': 'sector',
                'trend': sector_analysis['current_trend'],
                'confidence': trend_conf
            })
            confidence_scores.append(trend_conf)
        
        # Hot number prediction
        if hot_cold[0]:  # If there are hot numbers
            hot_nums = [n for n, _ in hot_cold[0][:3]]
            predictions.append({
                'type': 'hot_numbers',
                'numbers': hot_nums,
                'confidence': 0.5
            })
            confidence_scores.append(0.5)
        
        # Bias-based prediction
        if biases['bias_detected'] and biases['bias_groups']:
            max_group = max(biases['bias_groups'].items(), key=lambda x: len(x[1]))
            predictions.append({
                'type': 'bias',
                'numbers': max_group[1],
                'confidence': 0.6
            })
            confidence_scores.append(0.6)
        
        # Calculate overall confidence
        overall_confidence = np.mean(confidence_scores) if confidence_scores else 0
        
        return {
            'confidence': overall_confidence,
            'predictions': predictions if overall_confidence >= confidence_threshold else []
        }

    def get_number_properties(self, number: int) -> Dict:
        """Get comprehensive properties of a number"""
        if number not in self.number_mapping:
            raise ValueError(f"Invalid number: {number}")
            
        props = self.number_mapping[number].copy()
        props.update({
            'number': number,
            'is_even': number % 2 == 0 and number != 0,
            'is_odd': number % 2 == 1,
            'dozen': ((number - 1) // 12) + 1 if number != 0 else 0,
            'column': ((number - 1) % 3) + 1 if number != 0 else 0,
            'half': 'second' if number > 18 else 'first' if number > 0 else 'zero'
        })
        
        return props
