"""Test GameWith scraper"""
import sys
from pathlib import Path
import asyncio

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.scraper.gamewith_scraper import GameWithScraper
from app.core.logging import setup_logging

logger = setup_logging()

async def test():
    logger.info("Testing GameWith scraper...")
    
    async with GameWithScraper() as scraper:
        # Test character list
        logger.info("=== Testing character list scraping ===")
        chars = await scraper.scrape_character_list()
        logger.info(f"Found {len(chars)} characters")
        
        if chars:
            logger.info("\nFirst 3 characters:")
            for i, char in enumerate(chars[:3]):
                logger.info(f"{i+1}. {char}")

asyncio.run(test())
