import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import tensorflow as tf
from datetime import datetime, timedelta
import json
from ..database.database import DatabaseManager

class RouletteAnalyzer:
    def __init__(self):
        self.db = DatabaseManager()
        self.scaler = StandardScaler()
        self.models = {
            'random_forest': None,
            'neural_network': None
        }
        self.feature_importance = {}
        
    def prepare_features(self, numbers, window_size=10):
        """Prepare features for prediction"""
        features = []
        targets = []
        
        for i in range(len(numbers) - window_size):
            # Historical numbers
            window = numbers[i:i+window_size]
            
            # Calculate features
            feature_vector = [
                np.mean(window),  # Average
                np.std(window),   # Standard deviation
                max(window),      # Maximum
                min(window),      # Minimum
                self._calculate_sector_ratios(window),  # Sector distribution
                self._calculate_color_ratios(window),   # Color distribution
                self._calculate_even_odd_ratio(window), # Even/Odd ratio
                self._calculate_high_low_ratio(window)  # High/Low ratio
            ]
            
            features.append(feature_vector)
            targets.append(numbers[i+window_size])
            
        return np.array(features), np.array(targets)
        
    def _calculate_sector_ratios(self, numbers):
        """Calculate ratios of numbers in different sectors"""
        sectors = {
            'first_12': sum(1 for n in numbers if 1 <= n <= 12),
            'second_12': sum(1 for n in numbers if 13 <= n <= 24),
            'third_12': sum(1 for n in numbers if 25 <= n <= 36),
            'zero': sum(1 for n in numbers if n == 0)
        }
        total = len(numbers)
        return [count/total for count in sectors.values()]
        
    def _calculate_color_ratios(self, numbers):
        """Calculate red/black ratios"""
        red_numbers = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
        red_count = sum(1 for n in numbers if n in red_numbers)
        black_count = sum(1 for n in numbers if n > 0 and n not in red_numbers)
        total = len(numbers)
        return [red_count/total, black_count/total]
        
    def _calculate_even_odd_ratio(self, numbers):
        """Calculate even/odd ratio"""
        even_count = sum(1 for n in numbers if n > 0 and n % 2 == 0)
        return even_count / len(numbers)
        
    def _calculate_high_low_ratio(self, numbers):
        """Calculate high/low number ratio"""
        high_count = sum(1 for n in numbers if n > 18)
        return high_count / len(numbers)
        
    def train_models(self, training_data=None):
        """Train prediction models"""
        try:
            if training_data is None:
                # Get data from database
                data = self.db.get_website_data(url='roulette_spins')
                if not data:
                    raise ValueError("No training data available")
                    
                numbers = [d.content['number'] for d in data]
            else:
                numbers = training_data
                
            # Prepare features
            X, y = self.prepare_features(numbers)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Random Forest
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            rf_model.fit(X_train_scaled, y_train)
            rf_pred = rf_model.predict(X_test_scaled)
            rf_accuracy = accuracy_score(y_test, rf_pred)
            
            # Train Neural Network
            nn_model = tf.keras.Sequential([
                tf.keras.layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(32, activation='relu'),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(37, activation='softmax')  # 37 possible outcomes (0-36)
            ])
            
            nn_model.compile(optimizer='adam',
                           loss='sparse_categorical_crossentropy',
                           metrics=['accuracy'])
                           
            nn_model.fit(X_train_scaled, y_train, epochs=50, batch_size=32, verbose=0)
            nn_accuracy = nn_model.evaluate(X_test_scaled, y_test, verbose=0)[1]
            
            # Store models
            self.models['random_forest'] = rf_model
            self.models['neural_network'] = nn_model
            
            # Calculate feature importance
            self.feature_importance = {
                'random_forest': dict(zip(range(X_train.shape[1]), rf_model.feature_importances_))
            }
            
            # Save models to database
            self._save_model('random_forest', rf_model, {'accuracy': rf_accuracy})
            self._save_model('neural_network', nn_model, {'accuracy': nn_accuracy})
            
            return {
                'random_forest_accuracy': rf_accuracy,
                'neural_network_accuracy': nn_accuracy,
                'feature_importance': self.feature_importance
            }
            
        except Exception as e:
            print(f"Error training models: {str(e)}")
            return None
            
    def predict_next(self, recent_numbers, model_type='ensemble'):
        """Predict next number"""
        try:
            if len(recent_numbers) < 10:
                raise ValueError("Need at least 10 recent numbers for prediction")
                
            # Prepare features
            X, _ = self.prepare_features([recent_numbers[-10:]])
            X_scaled = self.scaler.transform(X)
            
            predictions = {}
            probabilities = {}
            
            if model_type in ['random_forest', 'ensemble']:
                rf_pred = self.models['random_forest'].predict(X_scaled)
                rf_prob = self.models['random_forest'].predict_proba(X_scaled)
                predictions['random_forest'] = int(rf_pred[0])
                probabilities['random_forest'] = rf_prob[0]
                
            if model_type in ['neural_network', 'ensemble']:
                nn_prob = self.models['neural_network'].predict(X_scaled)[0]
                nn_pred = np.argmax(nn_prob)
                predictions['neural_network'] = int(nn_pred)
                probabilities['neural_network'] = nn_prob
                
            if model_type == 'ensemble':
                # Combine predictions using weighted average of probabilities
                combined_prob = (probabilities['random_forest'] + probabilities['neural_network']) / 2
                ensemble_pred = np.argmax(combined_prob)
                predictions['ensemble'] = int(ensemble_pred)
                probabilities['ensemble'] = combined_prob
                
            return {
                'predictions': predictions,
                'probabilities': probabilities,
                'confidence_metrics': self._calculate_confidence_metrics(probabilities[model_type])
            }
            
        except Exception as e:
            print(f"Error making prediction: {str(e)}")
            return None
            
    def _calculate_confidence_metrics(self, probabilities):
        """Calculate confidence metrics for predictions"""
        return {
            'entropy': -np.sum(probabilities * np.log2(probabilities + 1e-10)),
            'max_probability': np.max(probabilities),
            'top_3_numbers': np.argsort(probabilities)[-3:][::-1].tolist(),
            'top_3_probabilities': np.sort(probabilities)[-3:][::-1].tolist()
        }
        
    def _save_model(self, name, model, metrics):
        """Save model to database"""
        model_data = {
            'type': name,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        self.db.save_ml_model(
            name=name,
            model_type='roulette_prediction',
            parameters=model_data,
            metrics=metrics
        )
        
    def analyze_prediction_accuracy(self, window_size=100):
        """Analyze prediction accuracy over time"""
        try:
            data = self.db.get_website_data(url='roulette_spins')
            if not data or len(data) < window_size:
                return None
                
            numbers = [d.content['number'] for d in data]
            predictions = []
            
            for i in range(len(numbers) - window_size):
                window = numbers[i:i+window_size]
                pred = self.predict_next(window)
                if pred:
                    actual = numbers[i+window_size]
                    predictions.append({
                        'actual': actual,
                        'predicted': pred['predictions'],
                        'accuracy': any(p == actual for p in pred['predictions'].values())
                    })
                    
            return {
                'total_predictions': len(predictions),
                'accuracy_rate': sum(p['accuracy'] for p in predictions) / len(predictions),
                'prediction_history': predictions
            }
            
        except Exception as e:
            print(f"Error analyzing prediction accuracy: {str(e)}")
            return None
