import threading
import queue
import json
import logging
from datetime import datetime
from pathlib import Path
from .system_agent import SystemAgent

class AgentInterface:
    def __init__(self):
        self.setup_logging()
        self.system_agent = SystemAgent()
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.is_running = False
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path.home() / 'AppData' / 'Local' / 'AI_OS' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'agent_interface_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def start(self):
        """Start the agent interface"""
        self.is_running = True
        
        # Start command processing thread
        threading.Thread(target=self._process_loop, daemon=True).start()
        
        logging.info("Agent interface started")
        print("Agent interface is running. You can:")
        print("1. Type commands directly")
        print("2. Press Ctrl+C to exit")
        
    def stop(self):
        """Stop the agent interface"""
        self.is_running = False
        logging.info("Agent interface stopped")
        
    def _process_loop(self):
        """Main processing loop"""
        while self.is_running:
            try:
                # Check for typed commands
                try:
                    typed_command = self.command_queue.get_nowait()
                    self._handle_command(typed_command, source='typed')
                except queue.Empty:
                    pass
                    
            except Exception as e:
                logging.error(f"Error in process loop: {str(e)}")
                
    def _handle_command(self, command, source='typed'):
        """Handle a command from any source"""
        try:
            logging.info(f"Processing {source} command: {command}")
            
            # Process command with system agent
            result = self.system_agent.process_command(command)
            
            # Format response
            response = self._format_response(result)
            
            # Send response
            print(f"\nResponse: {response}")
                
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            logging.error(error_msg)
            print(f"\nError: {error_msg}")
                
    def _format_response(self, result):
        """Format the response for output"""
        try:
            if isinstance(result, str):
                return result
                
            elif isinstance(result, dict):
                return json.dumps(result, indent=2)
                
            elif isinstance(result, list):
                if all(isinstance(x, tuple) for x in result):  # Search results
                    return "Found these matches:\n" + "\n".join(
                        f"- {path} (similarity: {similarity:.2f})" 
                        for path, similarity in result
                    )
                else:
                    return json.dumps(result, indent=2)
                    
            else:
                return str(result)
                
        except Exception as e:
            logging.error(f"Error formatting response: {str(e)}")
            return str(result)
            
    def send_command(self, command):
        """Send a command to be processed"""
        self.command_queue.put(command)
        
if __name__ == "__main__":
    # Test the agent interface
    interface = AgentInterface()
    interface.start()
    
    try:
        while True:
            command = input("\nEnter command (or 'exit' to quit): ")
            if command.lower() == 'exit':
                break
            interface.send_command(command)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        
    finally:
        interface.stop()
