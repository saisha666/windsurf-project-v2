# Voice-Enabled Project

A Python project that combines voice interaction, web scraping, and AI capabilities.

## Project Structure

```
windsurf-project/
├── src/
│   ├── voice/              # Voice-related components
│   │   ├── agent.py           # Basic voice agent
│   │   ├── enhanced_voice_agent.py  # Agent with Eleven Labs
│   │   └── voice_to_text.py   # Speech-to-text converter
│   ├── scrapers/           # Web scraping components
│   │   ├── scraper.py         # Basic web scraper
│   │   └── sports_scraper.py  # Sports data scraper
│   ├── config/            # Configuration files
│   │   └── .env             # Environment variables
│   └── main.py           # Main entry point
├── tests/               # Test files
├── logs/               # Log files
├── requirements.txt    # Project dependencies
└── README.md          # Project documentation
```

## Features

1. **Voice Agent (Basic)**
   - Speech-to-text conversion
   - Basic text responses
   - Text-to-speech output

2. **Enhanced Voice Agent**
   - Uses Eleven Labs for high-quality AI voice
   - Improved conversation handling
   - Customizable voices

3. **Voice to Text Converter**
   - Standalone speech-to-text tool
   - Real-time conversion
   - Console output

4. **Web Scrapers**
   - Basic web scraping functionality
   - Sports data scraping
   - Data visualization

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure environment variables in `src/config/.env`

3. Run the project:
   ```
   python src/main.py
   ```

## Usage

Run `main.py` and choose which component you want to use:
1. Voice Agent (Basic)
2. Enhanced Voice Agent (with Eleven Labs)
3. Voice to Text Converter
4. Web Scraper
5. Sports Scraper
