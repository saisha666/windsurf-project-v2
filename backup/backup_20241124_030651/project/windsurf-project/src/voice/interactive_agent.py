import speech_recognition as sr
import pyttsx3
import json
import time
from typing import Optional, Dict, List
import threading
import queue
import keyboard

class InteractiveAgent:
    def __init__(self):
        """Initialize the interactive agent with both voice and text capabilities"""
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)    # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume
        
        # Communication mode
        self.voice_input_enabled = True
        self.voice_output_enabled = True
        
        # Input queue for handling both voice and text input
        self.input_queue = queue.Queue()
        
        # Command history
        self.command_history: List[Dict] = []
        
        print("\n=== Interactive AI Agent ===")
        print("Features:")
        print("- Press 'v' to toggle voice input (currently ON)")
        print("- Press 's' to toggle speech output (currently ON)")
        print("- Type 'history' to see command history")
        print("- Type 'quit' or say 'goodbye' to exit")
        print("- Press 'Ctrl+C' to force quit")
        print("=" * 25 + "\n")

    def toggle_voice_input(self):
        """Toggle voice input on/off"""
        self.voice_input_enabled = not self.voice_input_enabled
        status = "ON" if self.voice_input_enabled else "OFF"
        print(f"\nVoice input turned {status}")

    def toggle_voice_output(self):
        """Toggle voice output on/off"""
        self.voice_output_enabled = not self.voice_output_enabled
        status = "ON" if self.voice_output_enabled else "OFF"
        print(f"\nVoice output turned {status}")

    def listen_for_voice(self) -> Optional[str]:
        """Listen for voice input and convert to text"""
        try:
            with sr.Microphone() as source:
                print("\nListening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source)
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"\nVoice Input: {text}")
                    return text
                except sr.UnknownValueError:
                    print("Could not understand audio")
                    return None
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                    return None
        except Exception as e:
            print(f"Error with microphone: {e}")
            return None

    def speak(self, text: str):
        """Convert text to speech"""
        print(f"\nAI: {text}")
        if self.voice_output_enabled:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Error with text-to-speech: {e}")

    def process_input(self, text: str) -> str:
        """Process user input and generate response"""
        if not text:
            return "I didn't catch that. Could you please repeat?"
        
        # Convert to lowercase for processing
        text = text.lower()
        
        # Add to command history
        self.command_history.append({
            'input': text,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Handle special commands
        if text == 'history':
            history = "\nCommand History:\n"
            for cmd in self.command_history[-10:]:  # Show last 10 commands
                history += f"{cmd['timestamp']}: {cmd['input']}\n"
            return history
        
        # Basic conversation handling
        if 'hello' in text or 'hi' in text:
            return "Hello! How can I help you today?"
        elif 'how are you' in text:
            return "I'm doing great! Thanks for asking. How are you?"
        elif 'goodbye' in text or 'bye' in text or text == 'quit':
            return "Goodbye! Have a great day!"
        elif 'weather' in text:
            return "I can't check the weather yet, but I can help you with conversation!"
        elif 'name' in text:
            return "I'm your interactive AI assistant. You can talk to me through voice or text!"
        elif 'help' in text:
            return ("I can help you with basic conversation. Try saying hello, asking how I am, "
                   "or ask about my name. You can also type 'history' to see past commands.")
        else:
            return f"I heard: '{text}'. What would you like to know about that?"

    def voice_input_thread(self):
        """Thread for handling voice input"""
        while True:
            if self.voice_input_enabled:
                text = self.listen_for_voice()
                if text:
                    self.input_queue.put(text)
            time.sleep(0.1)  # Small delay to prevent CPU overuse

    def run(self):
        """Main loop for the interactive agent"""
        # Start voice input thread
        voice_thread = threading.Thread(target=self.voice_input_thread, daemon=True)
        voice_thread.start()
        
        # Set up keyboard handlers
        keyboard.on_press_key('v', lambda _: self.toggle_voice_input())
        keyboard.on_press_key('s', lambda _: self.toggle_voice_output())
        
        self.speak("Hello! I'm your interactive AI assistant. You can type or speak to me!")
        
        while True:
            try:
                # Check for voice input
                try:
                    voice_input = self.input_queue.get_nowait()
                    response = self.process_input(voice_input)
                    self.speak(response)
                    if voice_input.lower() in ['goodbye', 'bye', 'quit']:
                        break
                except queue.Empty:
                    pass
                
                # Check for text input
                if keyboard.is_pressed('enter'):
                    text_input = input("\nType your message: ")
                    if text_input.strip():
                        response = self.process_input(text_input)
                        self.speak(response)
                        if text_input.lower() in ['goodbye', 'bye', 'quit']:
                            break
                
                time.sleep(0.1)  # Small delay to prevent CPU overuse
                
            except KeyboardInterrupt:
                print("\nStopping the agent...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)

def main():
    agent = InteractiveAgent()
    agent.run()

if __name__ == "__main__":
    main()
