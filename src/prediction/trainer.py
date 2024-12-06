from preprocessor import DataPreprocessor
from agent import PredictionAgent
import json
import os
import logging
from datetime import datetime

def setup_logging():
    """Setup logging configuration"""
    log_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'RouletteData', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'training_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def train_models():
    """Train and evaluate prediction models"""
    setup_logging()
    logging.info("Starting model training process...")
    
    try:
        # Initialize preprocessor and agent
        preprocessor = DataPreprocessor()
        agent = PredictionAgent()
        
        # Load and preprocess data
        logging.info("Loading and preprocessing data...")
        data = preprocessor.preprocess_data()
        logging.info(f"Loaded {len(data)} records")
        
        # Train models
        logging.info("Training models...")
        accuracies = agent.train_models(data)
        
        # Log accuracies
        logging.info("Training completed. Model accuracies:")
        for model, acc in accuracies.items():
            logging.info(f"{model}: {acc:.4f}")
            
        # Save models
        logging.info("Saving models...")
        agent.save_models()
        
        # Test predictions
        logging.info("Testing predictions...")
        recent_numbers = data['number'].iloc[-10:].tolist()
        test_data = preprocessor.prepare_recent_data(recent_numbers)
        predictions = agent.predict(test_data)
        
        logging.info("Sample predictions:")
        for pred in predictions:
            logging.info(f"Number: {pred['number']}, "
                        f"Probability: {pred['probability']:.4f}, "
                        f"Confidence: {pred['confidence']}")
                        
        return True
        
    except Exception as e:
        logging.error(f"Error during training: {str(e)}")
        return False

if __name__ == "__main__":
    train_models()
