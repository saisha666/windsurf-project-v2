chmod +x Main.py2rpy

./install.sh

import sys
import logging
import threading
from pathlib import Path
from agents.agent_interface import AgentInterface
from api.server import start_server
from database.database import DatabaseManager
from scrapers.advanced_scraper import AdvancedScraper
from scrapers.roulette_collector import RouletteDataCollector
from analysis.roulette_analyzer import RouletteAnalyzer
from utils.installation_manager import InstallationManager

class System:
    def __init__(self):
        self.installation_manager = InstallationManager()
        self.installation_manager._load_config()
        self.current_drive = self._get_primary_drive()
        
    def _get_primary_drive(self):
        """Get the primary installation drive"""
        installations = self.installation_manager.list_installations()
        for install in installations:
            if install.get('is_primary', False):
                return install['drive']
        return None
    
    def get_base_path(self):
        """Get the base path for the current installation"""
        if self.current_drive:
            return Path(f"{self.current_drive}:/AI_OS")
        return None
    
    def switch_installation(self, drive: str):
        """Switch to a different installation"""
        if self.installation_manager.get_installation_info(drive):
            self.current_drive = drive
            return True
        return False

def setup_environment():
    """Setup the environment for the system"""
    # Add src directory to Python path
    src_dir = os.path.dirname(os.path.abspath(__file__))
    if src_dir not in sys.path:
        sys.path.append(src_dir)
        
    # Create necessary directories
    app_dir = Path.home() / 'AppData' / 'Local' / 'AI_OS'
    for subdir in ['logs', 'data', 'cache', 'config', 'models']:
        (app_dir / subdir).mkdir(parents=True, exist_ok=True)
        
def main():
    """Main entry point for the system"""
    try:
        # Initialize system
        system = System()
        if not system.current_drive:
            print("No primary installation found. Please run install.py first.")
            return 1
            
        # Setup environment
        setup_environment()
        
        # Initialize components with correct paths
        base_path = system.get_base_path()
        db = DatabaseManager(base_path / "data/database")
        scraper = AdvancedScraper()
        interface = AgentInterface()
        roulette_collector = RouletteDataCollector()
        roulette_analyzer = RouletteAnalyzer()
        
        # Start API server in a separate thread
        api_thread = threading.Thread(target=start_server, daemon=True)
        api_thread.start()
        
        # Start agent interface
        interface.start()
        
        print("\nWelcome to the AI Operating System!")
        print("\nAvailable interfaces:")
        print("1. Voice commands (say 'hey system' first)")
        print("2. Text commands")
        print("3. API (http://localhost:8000)")
        print("4. WebSocket (ws://localhost:8000/ws)")
        
        print("\nAvailable commands:")
        print("- search/find [query]: Search files semantically")
        print("- analyze [path/url]: Analyze a project directory or webpage")
        print("- research [topic]: Research a topic online")
        print("- scrape [url]: Scrape and analyze a website")
        print("- predict [model] [data]: Make predictions using ML models")
        print("\nRoulette Analysis Commands:")
        print("- collect roulette [url] [duration]: Collect live roulette data")
        print("- analyze patterns: Analyze collected roulette patterns")
        print("- train model: Train prediction models")
        print("- predict next: Predict next number")
        print("- show accuracy: Show prediction accuracy")
        print("\nInstallation Commands:")
        print("- switch [drive]: Switch to different installation")
        print("- sync [source] [target]: Sync between installations")
        print("- status: Show installation status")
        print("\nPress Ctrl+C to exit")
        
        # Main command loop
        while True:
            try:
                command = input("\nEnter command: ").strip()
                if command.lower() == 'exit':
                    break
                    
                # Process command
                if command.startswith('scrape '):
                    url = command[7:].strip()
                    print(f"Scraping {url}...")
                    result = scraper.scrape_url(url)
                    if result:
                        print("Scraping successful!")
                        
                elif command.startswith('collect roulette '):
                    parts = command.split()
                    if len(parts) >= 4:
                        url = parts[2]
                        duration = int(parts[3])
                        print(f"Collecting roulette data from {url} for {duration} minutes...")
                        data = roulette_collector.collect_live_data(url, duration)
                        if data is not None:
                            print(f"Collected {len(data)} spins!")
                            
                elif command == 'analyze patterns':
                    print("Analyzing roulette patterns...")
                    stats = roulette_analyzer.analyze_historical_data()
                    if stats:
                        print("\nAnalysis Results:")
                        print(f"Total Spins: {stats['total_spins']}")
                        print("\nHot Numbers:", sorted(stats['number_frequency'].items(), 
                                                     key=lambda x: x[1], reverse=True)[:5])
                        print("\nSector Trends:", stats['patterns']['sector_trends'])
                        
                elif command == 'train model':
                    print("Training prediction models...")
                    results = roulette_analyzer.train_models()
                    if results:
                        print("\nTraining Results:")
                        print(f"Random Forest Accuracy: {results['random_forest_accuracy']:.2%}")
                        print(f"Neural Network Accuracy: {results['neural_network_accuracy']:.2%}")
                        
                elif command == 'predict next':
                    data = db.get_website_data(url='roulette_spins')
                    if data:
                        numbers = [d.content['number'] for d in data][-10:]
                        print("\nMaking prediction based on:", numbers)
                        prediction = roulette_analyzer.predict_next(numbers)
                        if prediction:
                            print("\nPredictions:")
                            for model, number in prediction['predictions'].items():
                                print(f"{model}: {number}")
                            print("\nConfidence Metrics:")
                            print(f"Top 3 Numbers: {prediction['confidence_metrics']['top_3_numbers']}")
                            print(f"Top 3 Probabilities: {[f'{p:.2%}' for p in prediction['confidence_metrics']['top_3_probabilities']]}")
                            
                elif command == 'show accuracy':
                    print("Analyzing prediction accuracy...")
                    accuracy = roulette_analyzer.analyze_prediction_accuracy()
                    if accuracy:
                        print(f"\nOverall Accuracy Rate: {accuracy['accuracy_rate']:.2%}")
                        print(f"Total Predictions: {accuracy['total_predictions']}")
                        
                elif command.startswith('switch '):
                    drive = command.split()[1].upper()
                    if system.switch_installation(drive):
                        print(f"Switched to installation on drive {drive}")
                        # Reinitialize components with new paths
                        base_path = system.get_base_path()
                        db = DatabaseManager(base_path / "data/database")
                    else:
                        print(f"No installation found on drive {drive}")
                        
                elif command.startswith('sync '):
                    parts = command.split()
                    if len(parts) >= 3:
                        source = parts[1].upper()
                        target = parts[2].upper()
                        if system.installation_manager.sync_installations(source, target):
                            print("Synchronization completed successfully")
                        else:
                            print("Synchronization failed")
                            
                elif command == 'status':
                    installations = system.installation_manager.list_installations()
                    print("\nInstallation Status:")
                    for install in installations:
                        print(f"\nDrive {install['drive']}:")
                        print(f"Name: {install['name']}")
                        print(f"Primary: {install['is_primary']}")
                        print(f"Status: {install['status']}")
                        print(f"Sync Enabled: {install['sync_enabled']}")
                        validation = system.installation_manager.validate_installation(install['drive'])
                        print(f"Space Available: {validation['space_available'] // (1024*1024*1024)}GB")
                        
                else:
                    interface.send_command(command)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error(f"Error processing command: {str(e)}")
                print(f"Error: {str(e)}")
                
    except Exception as e:
        logging.error(f"System error: {str(e)}")
        print(f"System error: {str(e)}")
        
    finally:
        print("\nShutting down...")
        interface.stop()
        scraper.close()
        roulette_collector.close()
        
if __name__ == "__main__":
    main()
