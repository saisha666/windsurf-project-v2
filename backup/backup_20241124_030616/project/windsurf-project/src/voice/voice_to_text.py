import speech_recognition as sr
import time

def listen_and_convert():
    """
    Continuously listen for voice input and convert it to text.
    Press Ctrl+C to stop.
    """
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    print("Voice-to-Text Converter is running...")
    print("Speak into your microphone. Press Ctrl+C to stop.")
    print("-" * 50)
    
    while True:
        try:
            # Use microphone as source
            with sr.Microphone() as source:
                print("\nListening...")
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Listen for audio input
                audio = recognizer.listen(source)
                
                try:
                    # Convert speech to text using Google's speech recognition
                    text = recognizer.recognize_google(audio)
                    print("\nYou said:", text)
                    print("-" * 50)
                    
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                    
        except KeyboardInterrupt:
            print("\nStopping voice-to-text converter...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    listen_and_convert()
