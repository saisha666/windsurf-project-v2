""
  cmd = "top -bn1 | grep 'Cpu\|Mem'"
Traceback (most recent call last):
  File "c:\Users\shaonsai\CascadeProjects\windsurf-project\r_training_control.rpy2", line 1, in <module>
    import rpy2.robjects as robjects
ModuleNotFoundError: No module named 'rpy2'
import rpy2.robjectsimport numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import torch
import torch.nn as nn
from collections import deque
import joblib
from sklearn.cluster import DBSCAN
from scipy.stats import entropy
import json

@dataclass
class MemoryPattern:
    pattern_type: str  # flash, short, mid, long, mirror
    timestamp: datetime
    data: List[int]
    confidence: float
    duration: timedelta
    repeats: int
    
class AdvancedMemoryNetwork(nn.Module):
    """Neural network for pattern recognition in different memory types"""
    
    def __init__(self, input_size: int, hidden_size: int = 128):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers=2, batch_first=True)
        self.attention = nn.MultiheadAttention(hidden_size, num_heads=4)
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, input_size)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x, hidden=None):
        lstm_out, hidden = self.lstm(x, hidden)
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        x = self.dropout(attn_out)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x, hidden

class GameMemoryAnalyzer:
    """Advanced game and memory pattern analyzer"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.flash_memory = deque(maxlen=100)  # Last 100 flash patterns
        self.short_memory = deque(maxlen=1000)  # Last 1000 short patterns
        self.mid_memory = deque(maxlen=10000)   # Last 10000 mid patterns
        self.long_memory = []  # Unlimited long-term memory
        self.mirror_patterns = {}  # Mirror pattern storage
        
        # Initialize neural network
        self.network = AdvancedMemoryNetwork(input_size=37)  # For roulette numbers
        if model_path:
            self.network.load_state_dict(torch.load(model_path))
        self.network.eval()
        
        # Pattern tracking
        self.active_patterns = {}
        self.pattern_history = []
        self.confidence_threshold = 0.7
        
        # Initialize memory banks
        self.memory_banks = {
            'flash': {'duration': timedelta(seconds=5), 'patterns': deque(maxlen=100)},
            'short': {'duration': timedelta(minutes=5), 'patterns': deque(maxlen=1000)},
            'mid': {'duration': timedelta(hours=1), 'patterns': deque(maxlen=10000)},
            'long': {'duration': timedelta(days=30), 'patterns': []},
            'mirror': {'patterns': {}}
        }
        
    def analyze_sequence(self, numbers: List[int], 
                        timestamp: datetime = None) -> Dict[str, List[MemoryPattern]]:
        """Analyze a sequence for different types of memory patterns"""
        if timestamp is None:
            timestamp = datetime.now()
            
        patterns = {
            'flash': [],
            'short': [],
            'mid': [],
            'long': [],
            'mirror': []
        }
        
        # Convert to tensor
        sequence = torch.tensor(numbers, dtype=torch.float32).view(1, -1, 1)
        
        # Get network predictions
        with torch.no_grad():
            predictions, _ = self.network(sequence)
            
        # Analyze each memory type
        for memory_type in self.memory_banks:
            detected_patterns = self._analyze_memory_type(
                numbers, 
                memory_type, 
                timestamp,
                predictions
            )
            patterns[memory_type].extend(detected_patterns)
            
        # Update memory banks
        self._update_memory_banks(patterns, timestamp)
        
        return patterns
    
    def _analyze_memory_type(self, 
                           numbers: List[int], 
                           memory_type: str,
                           timestamp: datetime,
                           predictions: torch.Tensor) -> List[MemoryPattern]:
        """Analyze sequence for specific memory type patterns"""
        patterns = []
        
        if memory_type == 'flash':
            # Look for very recent, high-frequency patterns
            patterns.extend(self._detect_flash_patterns(numbers, timestamp))
            
        elif memory_type == 'mirror':
            # Look for mirror/reflection patterns
            patterns.extend(self._detect_mirror_patterns(numbers, timestamp))
            
        else:
            # Analyze temporal patterns based on memory type
            duration = self.memory_banks[memory_type]['duration']
            patterns.extend(
                self._detect_temporal_patterns(numbers, timestamp, duration)
            )
            
        return patterns
    
    def _detect_flash_patterns(self, 
                             numbers: List[int], 
                             timestamp: datetime) -> List[MemoryPattern]:
        """Detect very short-term flash patterns"""
        patterns = []
        
        # Use DBSCAN to cluster recent numbers
        if len(self.flash_memory) >= 10:
            recent_numbers = list(self.flash_memory)[-10:]
            clustering = DBSCAN(eps=3, min_samples=2).fit(
                np.array(recent_numbers).reshape(-1, 1)
            )
            
            # Analyze clusters
            for cluster_id in set(clustering.labels_):
                if cluster_id != -1:  # Skip noise
                    cluster_points = np.array(recent_numbers)[
                        clustering.labels_ == cluster_id
                    ]
                    
                    if len(cluster_points) >= 3:
                        confidence = len(cluster_points) / 10
                        patterns.append(MemoryPattern(
                            pattern_type='flash',
                            timestamp=timestamp,
                            data=cluster_points.tolist(),
                            confidence=confidence,
                            duration=timedelta(seconds=5),
                            repeats=len(cluster_points)
                        ))
                        
        return patterns
    
    def _detect_mirror_patterns(self, 
                              numbers: List[int], 
                              timestamp: datetime) -> List[MemoryPattern]:
        """Detect mirror/reflection patterns"""
        patterns = []
        
        # Check for number pairs that sum to 36 (mirror numbers in roulette)
        for i in range(len(numbers) - 1):
            for j in range(i + 1, len(numbers)):
                if numbers[i] + numbers[j] == 36:
                    confidence = 0.8 if j - i <= 3 else 0.6
                    patterns.append(MemoryPattern(
                        pattern_type='mirror',
                        timestamp=timestamp,
                        data=[numbers[i], numbers[j]],
                        confidence=confidence,
                        duration=timedelta(minutes=30),
                        repeats=2
                    ))
                    
        return patterns
    
    def _detect_temporal_patterns(self, 
                                numbers: List[int], 
                                timestamp: datetime,
                                duration: timedelta) -> List[MemoryPattern]:
        """Detect patterns over different time periods"""
        patterns = []
        
        # Analyze number frequencies
        number_freq = {}
        for num in numbers:
            number_freq[num] = number_freq.get(num, 0) + 1
            
        # Calculate entropy
        freqs = list(number_freq.values())
        pattern_entropy = entropy(freqs) if freqs else 0
        
        # Detect repeating sequences
        for length in range(2, min(len(numbers), 6)):
            for i in range(len(numbers) - length + 1):
                seq = tuple(numbers[i:i+length])
                
                # Check if sequence repeats
                repeats = 0
                for j in range(len(numbers) - length + 1):
                    if tuple(numbers[j:j+length]) == seq:
                        repeats += 1
                        
                if repeats >= 2:
                    confidence = min(0.9, (repeats * length) / len(numbers))
                    if confidence >= self.confidence_threshold:
                        patterns.append(MemoryPattern(
                            pattern_type='temporal',
                            timestamp=timestamp,
                            data=list(seq),
                            confidence=confidence,
                            duration=duration,
                            repeats=repeats
                        ))
                        
        return patterns
    
    def _update_memory_banks(self, 
                           patterns: Dict[str, List[MemoryPattern]], 
                           timestamp: datetime):
        """Update memory banks with new patterns"""
        for memory_type, memory_patterns in patterns.items():
            bank = self.memory_banks[memory_type]
            
            if memory_type == 'mirror':
                # Update mirror pattern storage
                for pattern in memory_patterns:
                    key = tuple(sorted(pattern.data))
                    if key not in bank['patterns']:
                        bank['patterns'][key] = []
                    bank['patterns'][key].append(pattern)
            else:
                # Update temporal pattern storage
                for pattern in memory_patterns:
                    bank['patterns'].append(pattern)
                    
                # Clean up old patterns (except long-term)
                if memory_type != 'long':
                    cutoff = timestamp - bank['duration']
                    bank['patterns'] = deque(
                        (p for p in bank['patterns'] 
                         if p.timestamp > cutoff),
                        maxlen=bank['patterns'].maxlen
                    )
    
    def get_active_patterns(self, 
                          timestamp: datetime = None) -> Dict[str, List[MemoryPattern]]:
        """Get currently active patterns"""
        if timestamp is None:
            timestamp = datetime.now()
            
        active = {memory_type: [] for memory_type in self.memory_banks}
        
        for memory_type, bank in self.memory_banks.items():
            if memory_type == 'mirror':
                # Check mirror patterns
                for patterns in bank['patterns'].values():
                    if patterns and (timestamp - patterns[-1].timestamp 
                                   < timedelta(minutes=30)):
                        active[memory_type].append(patterns[-1])
            else:
                # Check temporal patterns
                for pattern in bank['patterns']:
                    if (timestamp - pattern.timestamp < bank['duration'] and
                        pattern.confidence >= self.confidence_threshold):
                        active[memory_type].append(pattern)
                        
        return active
    
    def predict_next(self, 
                    active_patterns: Dict[str, List[MemoryPattern]]) -> Dict[str, float]:
        """Predict next numbers based on active patterns"""
        predictions = {}
        total_weight = 0
        
        # Weight for each memory type
        weights = {
            'flash': 1.0,
            'short': 0.8,
            'mid': 0.6,
            'long': 0.4,
            'mirror': 0.7
        }
        
        for memory_type, patterns in active_patterns.items():
            weight = weights[memory_type]
            
            for pattern in patterns:
                # Calculate pattern-specific weight
                pattern_weight = weight * pattern.confidence
                total_weight += pattern_weight
                
                # Get predicted numbers from pattern
                if memory_type == 'mirror':
                    # For mirror patterns, predict the complement
                    for num in pattern.data:
                        pred = 36 - num
                        predictions[pred] = predictions.get(pred, 0) + pattern_weight
                else:
                    # For temporal patterns, predict the next in sequence
                    for num in pattern.data:
                        predictions[num] = predictions.get(num, 0) + pattern_weight
                        
        # Normalize predictions
        if total_weight > 0:
            predictions = {
                num: prob/total_weight 
                for num, prob in predictions.items()
            }
            
        return predictions
    
    def save_model(self, path: str):
        """Save the neural network model"""
        torch.save(self.network.state_dict(), path)
        
    def load_model(self, path: str):
        """Load the neural network model"""
        self.network.load_state_dict(torch.load(path))
        self.network.eval()
