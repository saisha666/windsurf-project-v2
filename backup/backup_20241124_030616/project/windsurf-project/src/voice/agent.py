import speech_recognition as sr
import pyttsx3
import json
import logging
from typing import Optional
from datetime import datetime

class CommunicativeAgent:
    def __init__(self, voice_enabled: bool = True):
        """
        Initialize the agent with voice and text capabilities
        
        Args:
            voice_enabled (bool): Whether to enable voice features
        """
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        
        self.voice_enabled = voice_enabled
        
        # Initialize text-to-speech engine
        if self.voice_enabled:
            self.engine = pyttsx3.init()
            # Set properties
            self.engine.setProperty('rate', 150)    # Speed of speech
            self.engine.setProperty('volume', 0.9)  # Volume (0-1)
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        logging.info("Agent initialized successfully")
    
    def speak(self, text: str) -> None:
        """
        Convert text to speech
        
        Args:
            text (str): Text to be spoken
        """
        if self.voice_enabled:
            try:
                print(f"Agent: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                logging.error(f"Error in text-to-speech: {e}")
                print(f"Error speaking: {e}")
        else:
            print(f"Agent: {text}")
    
    def listen(self) -> Optional[str]:
        """
        Listen for voice input and convert to text
        
        Returns:
            str: Recognized text from speech, or None if recognition failed
        """
        if not self.voice_enabled:
            return input("You: ")
            
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source)
                
                text = self.recognizer.recognize_google(audio)
                print(f"You: {text}")
                return text
                
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None
        except Exception as e:
            logging.error(f"Error in speech recognition: {e}")
            return None
    
    def process_text(self, text: str) -> str:
        """
        Process text input and generate a response
        
        Args:
            text (str): Input text to process
            
        Returns:
            str: Response text
        """
        if not text:
            return "I didn't catch that. Could you please repeat?"
        
        # Convert to lowercase for easier processing
        text = text.lower()
        
        # Basic responses - you can expand this based on your needs
        if "hello" in text or "hi" in text:
            return "Hello! How can I help you today?"
        elif "how are you" in text:
            return "I'm doing well, thank you for asking!"
        elif "bye" in text or "goodbye" in text:
            return "Goodbye! Have a great day!"
        else:
            return "I heard you say: " + text
    
    def run(self):
        """
        Main loop for the agent
        """
        self.speak("Hello! I'm your assistant. How can I help you?")
        
        while True:
            # Listen for input
            text = self.listen()
            
            if text:
                # Process the input and get response
                response = self.process_text(text)
                
                # Speak the response
                self.speak(response)
                
                # Exit condition
                if "bye" in text.lower() or "goodbye" in text.lower():
                    break

def main():
    # Create and run the agent
    agent = CommunicativeAgent(voice_enabled=True)
    agent.run()

if __name__ == "__main__":
    main()
