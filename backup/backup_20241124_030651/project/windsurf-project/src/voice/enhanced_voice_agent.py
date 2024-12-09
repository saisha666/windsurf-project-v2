import speech_recognition as sr
import time
from elevenlabs import generate, play, set_api_key
from dotenv import load_dotenv
import os

class EnhancedVoiceAgent:
    def __init__(self):
        """Initialize the enhanced voice agent with Eleven Labs integration"""
        # Load environment variables
        load_dotenv()
        
        # Set up Eleven Labs API key
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        if self.api_key:
            set_api_key(self.api_key)
        else:
            print("Warning: ELEVENLABS_API_KEY not found in .env file")
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        print("Enhanced Voice Agent Initialized!")
        print("Features:")
        print("- Speech-to-Text: Using Google Speech Recognition")
        print("- Text-to-Speech: Using Eleven Labs AI Voice")
        print("-" * 50)
    
    def listen(self):
        """Listen for voice input and convert to text"""
        try:
            with sr.Microphone() as source:
                print("\nListening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source)
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    print("\nYou said:", text)
                    return text
                except sr.UnknownValueError:
                    print("Could not understand audio")
                    return None
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                    return None
                    
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def speak(self, text):
        """Convert text to speech using Eleven Labs"""
        try:
            if not self.api_key:
                print("AI Response:", text)
                return
                
            print("AI Response:", text)
            audio = generate(
                text=text,
                voice="Rachel",  # You can change this to any available voice
                model="eleven_monolingual_v1"
            )
            play(audio)
        except Exception as e:
            print(f"Error generating speech: {e}")
            print("Falling back to text output:", text)
    
    def process_input(self, text):
        """Process user input and generate response"""
        if not text:
            return "I didn't catch that. Could you please repeat?"
            
        text = text.lower()
        
        # Basic conversation handling
        if "hello" in text or "hi" in text:
            return "Hello! How can I help you today?"
        elif "how are you" in text:
            return "I'm doing great! Thanks for asking. How are you?"
        elif "bye" in text or "goodbye" in text:
            return "Goodbye! Have a great day!"
        else:
            return f"I heard you say: {text}. How can I help you with that?"
    
    def run(self):
        """Main loop for the enhanced voice agent"""
        self.speak("Hello! I'm your enhanced AI assistant with Eleven Labs voice. How can I help you?")
        
        while True:
            try:
                # Listen for input
                user_input = self.listen()
                
                if user_input:
                    # Process input and generate response
                    response = self.process_input(user_input)
                    
                    # Speak the response
                    self.speak(response)
                    
                    # Check for exit condition
                    if "bye" in user_input.lower() or "goodbye" in user_input.lower():
                        break
                        
            except KeyboardInterrupt:
                print("\nStopping the voice agent...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)

def main():
    agent = EnhancedVoiceAgent()
    agent.run()

if __name__ == "__main__":
    main()
