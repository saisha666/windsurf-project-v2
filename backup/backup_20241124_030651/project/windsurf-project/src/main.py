import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Load environment variables
load_dotenv(os.path.join(project_root, 'src', 'config', '.env'))

def main():
    print("Welcome to the Voice-Enabled Project!")
    print("\nAvailable components:")
    print("1. Voice Agent (Basic)")
    print("2. Enhanced Voice Agent (with Eleven Labs)")
    print("3. Voice to Text Converter")
    print("4. Web Scraper")
    print("5. Sports Scraper")
    
    choice = input("\nEnter the number of the component you want to run (1-5): ")
    
    try:
        choice = int(choice)
        if choice == 1:
            from src.voice.agent import main as agent_main
            agent_main()
        elif choice == 2:
            from src.voice.enhanced_voice_agent import main as enhanced_agent_main
            enhanced_agent_main()
        elif choice == 3:
            from src.voice.voice_to_text import listen_and_convert
            listen_and_convert()
        elif choice == 4:
            from src.scrapers.scraper import main as scraper_main
            scraper_main()
        elif choice == 5:
            from src.scrapers.sports_scraper import main as sports_scraper_main
            sports_scraper_main()
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
    except ValueError:
        print("Invalid input. Please enter a number.")
    except ImportError as e:
        print(f"Error importing component: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
