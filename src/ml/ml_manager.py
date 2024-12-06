import os
import json
from datetime import datetime
import numpy as np
from pathlib import Path
import joblib
from typing import Dict, List, Optional, Union
import tensorflow as tf
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
import logging

class MLManager:
    """Manages scalable ML/AI models with time-based analysis"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path / "models"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.models = {}
        self.model_metrics = {}
        self.training_history = {}
        
    def create_model(self, model_name: str, model_type: str, params: Dict = None) -> bool:
        """Create a new ML model"""
        try:
            if model_type == "random_forest":
                model = RandomForestClassifier(**(params or {}))
            elif model_type == "neural_network":
                model = MLPClassifier(**(params or {}))
            elif model_type == "deep_learning":
                model = self._create_deep_learning_model(params or {})
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
                
            self.models[model_name] = {
                "model": model,
                "type": model_type,
                "created_at": datetime.now().isoformat(),
                "last_trained": None,
                "version": "1.0"
            }
            return True
            
        except Exception as e:
            logging.error(f"Error creating model {model_name}: {str(e)}")
            return False
    
    def _create_deep_learning_model(self, params: Dict) -> tf.keras.Model:
        """Create a deep learning model with specified architecture"""
        input_shape = params.get("input_shape", (10,))
        layers = params.get("layers", [64, 32])
        
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Input(shape=input_shape))
        
        for units in layers:
            model.add(tf.keras.layers.Dense(units, activation='relu'))
            model.add(tf.keras.layers.Dropout(0.2))
            
        model.add(tf.keras.layers.Dense(37, activation='softmax'))  # For roulette numbers
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        return model
    
    def train_model(self, model_name: str, X: np.ndarray, y: np.ndarray, 
                   validation_split: float = 0.2) -> Dict:
        """Train a model with performance tracking"""
        try:
            model_info = self.models.get(model_name)
            if not model_info:
                raise ValueError(f"Model {model_name} not found")
                
            model = model_info["model"]
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=validation_split)
            
            # Train based on model type
            if model_info["type"] == "deep_learning":
                history = model.fit(
                    X_train, y_train,
                    validation_data=(X_val, y_val),
                    epochs=50,
                    batch_size=32,
                    verbose=0
                )
                metrics = {
                    "train_accuracy": float(history.history['accuracy'][-1]),
                    "val_accuracy": float(history.history['val_accuracy'][-1]),
                    "train_loss": float(history.history['loss'][-1]),
                    "val_loss": float(history.history['val_loss'][-1])
                }
            else:
                model.fit(X_train, y_train)
                train_score = model.score(X_train, y_train)
                val_score = model.score(X_val, y_val)
                metrics = {
                    "train_accuracy": float(train_score),
                    "val_accuracy": float(val_score)
                }
            
            # Update model information
            model_info["last_trained"] = datetime.now().isoformat()
            self.model_metrics[model_name] = metrics
            
            # Save training history
            self.training_history.setdefault(model_name, []).append({
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics,
                "samples": len(X)
            })
            
            # Save model and metrics
            self._save_model(model_name)
            return metrics
            
        except Exception as e:
            logging.error(f"Error training model {model_name}: {str(e)}")
            return {}
    
    def predict(self, model_name: str, X: np.ndarray, 
               return_proba: bool = False) -> Union[np.ndarray, Dict]:
        """Make predictions with confidence scores"""
        try:
            model_info = self.models.get(model_name)
            if not model_info:
                raise ValueError(f"Model {model_name} not found")
                
            model = model_info["model"]
            
            if return_proba:
                if hasattr(model, 'predict_proba'):
                    probabilities = model.predict_proba(X)
                    predictions = np.argmax(probabilities, axis=1)
                    confidence = np.max(probabilities, axis=1)
                    return {
                        "predictions": predictions,
                        "probabilities": probabilities,
                        "confidence": confidence
                    }
                else:
                    raise ValueError(f"Model {model_name} doesn't support probability predictions")
            else:
                return model.predict(X)
                
        except Exception as e:
            logging.error(f"Error making predictions with {model_name}: {str(e)}")
            return np.array([])
    
    def get_model_performance(self, model_name: str, 
                            time_range: Optional[tuple] = None) -> Dict:
        """Get model performance metrics over time"""
        try:
            history = self.training_history.get(model_name, [])
            if not history:
                return {}
                
            if time_range:
                start, end = time_range
                history = [
                    h for h in history 
                    if start <= datetime.fromisoformat(h["timestamp"]) <= end
                ]
                
            return {
                "accuracy_trend": [h["metrics"]["val_accuracy"] for h in history],
                "sample_sizes": [h["samples"] for h in history],
                "timestamps": [h["timestamp"] for h in history],
                "latest_metrics": history[-1]["metrics"] if history else None
            }
            
        except Exception as e:
            logging.error(f"Error getting performance for {model_name}: {str(e)}")
            return {}
    
    def _save_model(self, model_name: str):
        """Save model and its metadata"""
        try:
            model_info = self.models[model_name]
            model_dir = self.base_path / model_name
            model_dir.mkdir(exist_ok=True)
            
            # Save model
            if model_info["type"] == "deep_learning":
                model_info["model"].save(str(model_dir / "model"))
            else:
                joblib.dump(model_info["model"], model_dir / "model.joblib")
            
            # Save metadata
            metadata = {
                "type": model_info["type"],
                "created_at": model_info["created_at"],
                "last_trained": model_info["last_trained"],
                "version": model_info["version"],
                "metrics": self.model_metrics.get(model_name, {}),
                "history": self.training_history.get(model_name, [])
            }
            
            with open(model_dir / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=4)
                
        except Exception as e:
            logging.error(f"Error saving model {model_name}: {str(e)}")
    
    def load_model(self, model_name: str) -> bool:
        """Load a saved model and its metadata"""
        try:
            model_dir = self.base_path / model_name
            if not model_dir.exists():
                return False
                
            # Load metadata
            with open(model_dir / "metadata.json", 'r') as f:
                metadata = json.load(f)
                
            # Load model based on type
            if metadata["type"] == "deep_learning":
                model = tf.keras.models.load_model(str(model_dir / "model"))
            else:
                model = joblib.load(model_dir / "model.joblib")
                
            self.models[model_name] = {
                "model": model,
                "type": metadata["type"],
                "created_at": metadata["created_at"],
                "last_trained": metadata["last_trained"],
                "version": metadata["version"]
            }
            
            self.model_metrics[model_name] = metadata["metrics"]
            self.training_history[model_name] = metadata["history"]
            return True
            
        except Exception as e:
            logging.error(f"Error loading model {model_name}: {str(e)}")
            return False
