import numpy as np
import pandas as pd
import tensorflow as tf
import torch
import xgboost as xgb
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import optuna
from datetime import datetime, timedelta
import json
import os

class PredictionAgent:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.accuracy_history = []
        self.load_config()
        
    def load_config(self):
        """Load configuration settings"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'storage.json')
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
    def prepare_features(self, data):
        """Prepare features for prediction"""
        features = []
        
        # Time-based features
        features.extend([
            data['hour'].values,
            data['minute'].values,
            data['day_of_week'].values,
            np.sin(2 * np.pi * data['hour'].values / 24),  # Cyclical time
            np.cos(2 * np.pi * data['hour'].values / 24)
        ])
        
        # Sequence features
        for i in range(1, 6):  # Last 5 numbers
            features.append(data[f'prev_{i}'].values)
            
        # Pattern features
        features.extend([
            data['consecutive_same'].values,
            data['time_since_last'].values,
            data['spin_duration'].values
        ])
        
        # Provider features
        features.extend([
            data['provider_id'].values,
            data['table_id'].values
        ])
        
        return np.column_stack(features)
        
    def create_lstm_model(self, input_shape):
        """Create LSTM model for sequence prediction"""
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(128, input_shape=input_shape, return_sequences=True),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(64),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(37, activation='softmax')  # 0-36 numbers
        ])
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        return model
        
    def create_xgboost_model(self):
        """Create XGBoost model"""
        return xgb.XGBClassifier(
            n_estimators=1000,
            learning_rate=0.01,
            max_depth=7,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='multi:softprob',
            num_class=37
        )
        
    def create_lightgbm_model(self):
        """Create LightGBM model"""
        return lgb.LGBMClassifier(
            n_estimators=1000,
            learning_rate=0.01,
            max_depth=7,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='multiclass',
            num_class=37
        )
        
    def optimize_hyperparameters(self, X_train, y_train):
        """Optimize model hyperparameters using Optuna"""
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 500, 2000),
                'max_depth': trial.suggest_int('max_depth', 5, 12),
                'learning_rate': trial.suggest_loguniform('learning_rate', 1e-3, 1e-1),
                'subsample': trial.suggest_uniform('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_uniform('colsample_bytree', 0.6, 1.0)
            }
            
            model = xgb.XGBClassifier(**params, objective='multi:softprob', num_class=37)
            model.fit(X_train, y_train)
            return model.score(X_train, y_train)
            
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=100)
        return study.best_params
        
    def train_models(self, data):
        """Train all models"""
        X = self.prepare_features(data)
        y = data['number'].values
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        self.scalers['standard'] = StandardScaler()
        X_train_scaled = self.scalers['standard'].fit_transform(X_train)
        X_test_scaled = self.scalers['standard'].transform(X_test)
        
        # Train LSTM
        X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
        X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))
        
        self.models['lstm'] = self.create_lstm_model((1, X_train_scaled.shape[1]))
        self.models['lstm'].fit(X_train_lstm, y_train, epochs=50, batch_size=32, validation_split=0.2)
        
        # Optimize and train XGBoost
        best_params = self.optimize_hyperparameters(X_train_scaled, y_train)
        self.models['xgboost'] = xgb.XGBClassifier(**best_params, objective='multi:softprob', num_class=37)
        self.models['xgboost'].fit(X_train_scaled, y_train)
        
        # Train LightGBM
        self.models['lightgbm'] = self.create_lightgbm_model()
        self.models['lightgbm'].fit(X_train_scaled, y_train)
        
        # Calculate feature importance
        self.feature_importance['xgboost'] = self.models['xgboost'].feature_importances_
        self.feature_importance['lightgbm'] = self.models['lightgbm'].feature_importances_
        
        # Evaluate models
        accuracies = {
            'lstm': self.models['lstm'].evaluate(X_test_lstm, y_test)[1],
            'xgboost': self.models['xgboost'].score(X_test_scaled, y_test),
            'lightgbm': self.models['lightgbm'].score(X_test_scaled, y_test)
        }
        
        self.accuracy_history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'accuracies': accuracies
        })
        
        return accuracies
        
    def predict(self, data):
        """Make predictions using ensemble of models"""
        X = self.prepare_features(data)
        X_scaled = self.scalers['standard'].transform(X)
        X_lstm = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))
        
        # Get predictions from each model
        pred_lstm = self.models['lstm'].predict(X_lstm)
        pred_xgb = self.models['xgboost'].predict_proba(X_scaled)
        pred_lgb = self.models['lightgbm'].predict_proba(X_scaled)
        
        # Weighted ensemble
        ensemble_pred = (0.4 * pred_lstm + 0.3 * pred_xgb + 0.3 * pred_lgb)
        
        # Get top 3 predictions with probabilities
        top_3_idx = np.argsort(ensemble_pred[0])[-3:][::-1]
        predictions = [{
            'number': int(idx),
            'probability': float(ensemble_pred[0][idx]),
            'confidence': self.calculate_confidence(ensemble_pred[0][idx])
        } for idx in top_3_idx]
        
        return predictions
        
    def calculate_confidence(self, probability):
        """Calculate confidence level based on probability"""
        if probability > 0.8:
            return "Very High"
        elif probability > 0.6:
            return "High"
        elif probability > 0.4:
            return "Medium"
        else:
            return "Low"
            
    def save_models(self):
        """Save trained models and scalers"""
        save_dir = os.path.join(self.config['data_root'], 'models')
        os.makedirs(save_dir, exist_ok=True)
        
        # Save neural network
        self.models['lstm'].save(os.path.join(save_dir, 'lstm_model'))
        
        # Save tree-based models
        with open(os.path.join(save_dir, 'xgboost_model.json'), 'wb') as f:
            self.models['xgboost'].save_model(f)
            
        with open(os.path.join(save_dir, 'lightgbm_model.txt'), 'w') as f:
            f.write(self.models['lightgbm'].booster_.save_model_to_string())
            
        # Save scaler
        with open(os.path.join(save_dir, 'scaler.pkl'), 'wb') as f:
            import pickle
            pickle.dump(self.scalers['standard'], f)
            
    def load_models(self):
        """Load saved models and scalers"""
        load_dir = os.path.join(self.config['data_root'], 'models')
        
        try:
            # Load neural network
            self.models['lstm'] = tf.keras.models.load_model(os.path.join(load_dir, 'lstm_model'))
            
            # Load tree-based models
            self.models['xgboost'] = xgb.XGBClassifier()
            self.models['xgboost'].load_model(os.path.join(load_dir, 'xgboost_model.json'))
            
            self.models['lightgbm'] = lgb.LGBMClassifier()
            self.models['lightgbm'].booster_ = lgb.Booster(model_file=os.path.join(load_dir, 'lightgbm_model.txt'))
            
            # Load scaler
            with open(os.path.join(load_dir, 'scaler.pkl'), 'rb') as f:
                import pickle
                self.scalers['standard'] = pickle.load(f)
                
            return True
            
        except Exception as e:
            print(f"Error loading models: {str(e)}")
            return False
