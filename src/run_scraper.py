import asyncio
from scrapers.stealth_scraper import StealthScraper

async def main():
    scraper = StealthScraper()
    while True:
        try:
            await scraper.run("https://example.com")  # Replace with your target URL
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            await asyncio.sleep(10)  # Wait before retrying

if __name__ == "__main__":
    asyncio.run(main())
