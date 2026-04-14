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

from app.services.scraper.gamewith_scraper import scrape_gamewith
from app.services.scraper.wiki_scraper import scrape_wiki
from app.services.indexer import get_indexer
from app.core.logging import setup_logging

logger = setup_logging()


async def scrape_all_sources(
    use_gamewith: bool = True,
    use_wiki: bool = False,
    character_limit: int = None,
) -> List[Dict[str, Any]]:
    """
    Scrape from all configured sources.
    
    Args:
        use_gamewith: Whether to scrape GameWith (優先)
        use_wiki: Whether to scrape Wiki
        character_limit: Limit number of characters per source
        
    Returns:
        Combined list of scraped documents
    """
    all_documents = []
    
    # GameWith（優先度高）
    if use_gamewith:
        try:
            logger.info("=== Scraping GameWith (Priority Source) ===")
            gamewith_data = await scrape_gamewith(character_limit=character_limit)
            logger.info(f"GameWith: Scraped {len(gamewith_data)} items")
            all_documents.extend(gamewith_data)
        except Exception as e:
            logger.error(f"GameWith scraping failed: {e}")
    
    # Wiki（補足情報）
    if use_wiki:
        try:
            logger.info("=== Scraping Wiki (Supplementary Source) ===")
            wiki_data = await scrape_wiki()
            logger.info(f"Wiki: Scraped {len(wiki_data)} items")
            all_documents.extend(wiki_data)
        except Exception as e:
            logger.error(f"Wiki scraping failed: {e}")
    
    return all_documents


async def scrape_and_index(
    use_gamewith: bool = True,
    use_wiki: bool = False,
    character_limit: int = 10,
    dry_run: bool = False,
):
    """
    Scrape data and index into vector store.
    
    Args:
        use_gamewith: Scrape from GameWith
        use_wiki: Scrape from Wiki
        character_limit: Limit per source
        dry_run: If True, scrape but don't index
    """
    logger.info("Starting scrape and index process...")
    logger.info(f"Sources: GameWith={use_gamewith}, Wiki={use_wiki}")
    logger.info(f"Character limit: {character_limit}")
    logger.info(f"Dry run: {dry_run}")
    
    # Scrape data
    documents = await scrape_all_sources(
        use_gamewith=use_gamewith,
        use_wiki=use_wiki,
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
    parser.add_argument("--gamewith", action="store_true", default=True, help="Scrape GameWith (default: True)")
    parser.add_argument("--wiki", action="store_true", default=False, help="Scrape Wiki")
    parser.add_argument("--limit", type=int, default=10, help="Character limit per source (default: 10)")
    parser.add_argument("--dry-run", action="store_true", help="Scrape but don't index")
    parser.add_argument("--all", action="store_true", help="Scrape all characters (no limit)")
    
    args = parser.parse_args()
    
    limit = None if args.all else args.limit
    
    asyncio.run(scrape_and_index(
        use_gamewith=args.gamewith,
        use_wiki=args.wiki,
        character_limit=limit,
        dry_run=args.dry_run,
    ))
