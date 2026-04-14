"""
Master scraper script that coordinates all data sources.
"""
import sys
from pathlib import Path
import asyncio
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Use mock scraper for now (real scraper needs GameWith HTML structure)
from app.services.scraper.mock_scraper import scrape_gamewith_mock
from app.services.indexer import get_indexer
from app.core.logging import setup_logging

logger = setup_logging()


async def scrape_all_sources(
    character_limit: int = None,
) -> List[Dict[str, Any]]:
    """
    Scrape from all configured sources.
    
    Args:
        character_limit: Limit number of characters per source
        
    Returns:
        Combined list of scraped documents
    """
    all_documents = []
    
    # モックスクレイパーを使用（実際のGameWith構造確認後に実装）
    try:
        logger.info("=== Using Mock Scraper (Testing) ===")
        logger.info("NOTE: This uses sample data. Implement real scraper in gamewith_scraper.py")
        mock_data = await scrape_gamewith_mock(character_limit=character_limit)
        logger.info(f"Mock data: {len(mock_data)} items")
        all_documents.extend(mock_data)
    except Exception as e:
        logger.error(f"Mock scraper failed: {e}")
    
    return all_documents


async def scrape_and_index(
    character_limit: int = 10,
    dry_run: bool = False,
):
    """
    Scrape data and index into vector store.
    
    Args:
        character_limit: Limit per source
        dry_run: If True, scrape but don't index
    """
    logger.info("Starting scrape and index process...")
    logger.info(f"Character limit: {character_limit}")
    logger.info(f"Dry run: {dry_run}")
    logger.info("NOTE: Currently using MOCK data for testing")
    
    # Scrape data
    documents = await scrape_all_sources(
        character_limit=character_limit,
    )
    
    if not documents:
        logger.warning("No documents scraped!")
        return
    
    logger.info(f"Total scraped documents: {len(documents)}")
    
    # Show sample
    logger.info("\n=== Sample Data ===")
    for i, doc in enumerate(documents[:3]):
        logger.info(f"{i+1}. {doc.get('name', 'N/A')} ({doc.get('type', 'unknown')}) - Source: {doc.get('source', 'unknown')}")
        if doc.get('content'):
            content_preview = doc['content'][:100] + "..." if len(doc['content']) > 100 else doc['content']
            logger.info(f"   Preview: {content_preview}")
    
    if dry_run:
        logger.info("Dry run mode - skipping indexing")
        return
    
    # Index into vector store
    logger.info("\n=== Indexing Documents ===")
    indexer = get_indexer()
    
    # Format documents for indexer
    formatted_docs = []
    for doc in documents:
        formatted_doc = {
            "id": f"{doc.get('source', 'unknown')}_{doc.get('type', 'doc')}_{doc.get('name', 'unknown').replace(' ', '_')}",
            "type": doc.get("type", "unknown"),
            "name": doc.get("name", "Unknown"),
            "content": doc.get("content", ""),
            "element": doc.get("element"),
            "rarity": doc.get("rarity"),
            "tags": doc.get("tags", []),
            "source_url": doc.get("url"),
        }
        formatted_docs.append(formatted_doc)
    
    num_chunks = indexer.process_and_index(formatted_docs)
    
    logger.info(f"\n=== Complete! ===")
    logger.info(f"Indexed {num_chunks} chunks from {len(documents)} documents")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape Granblue Fantasy data")
    parser.add_argument("--limit", type=int, default=10, help="Character limit (default: 10)")
    parser.add_argument("--dry-run", action="store_true", help="Scrape but don't index")
    
    args = parser.parse_args()
    
    asyncio.run(scrape_and_index(
        character_limit=args.limit,
        dry_run=args.dry_run,
    ))
