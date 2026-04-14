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

# Use file-based scraper (works without Playwright/requests - uses local HTML)
from app.services.scraper.gamewith_file_scraper import scrape_gamewith_from_file as scrape_gamewith
from app.services.indexer import get_indexer
from app.core.logging import setup_logging

logger = setup_logging()


async def scrape_all_sources(
    character_limit: int = None,
) -> List[Dict[str, Any]]:
    """
    Scrape from GameWith.
    
    Args:
        character_limit: Limit number of characters
        
    Returns:
        List of scraped documents
    """
    all_documents = []
    
    # GameWith実スクレイパーを使用
    try:
        logger.info("=== Scraping GameWith (Real Scraper) ===")
        gamewith_data = await scrape_gamewith(character_limit=character_limit)
        logger.info(f"GameWith: Scraped {len(gamewith_data)} items")
        all_documents.extend(gamewith_data)
    except Exception as e:
        logger.error(f"GameWith scraping failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
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
    logger.info("Using REAL GameWith scraper")
    
    # Scrape data
    documents = await scrape_all_sources(
        character_limit=character_limit,
    )
    
    if not documents:
        logger.warning("No documents scraped!")
        return
    
    logger.info(f"Total scraped documents: {len(documents)}")
    
    # Show detailed preview
    logger.info("\n" + "="*80)
    logger.info("=== SCRAPED DATA PREVIEW ===")
    logger.info("="*80)
    
    for i, doc in enumerate(documents[:5]):  # 最初の5件を詳細表示
        logger.info(f"\n[{i+1}] {doc.get('name', 'N/A')}")
        logger.info(f"    Type: {doc.get('type', 'unknown')}")
        logger.info(f"    Element: {doc.get('element', 'N/A')}")
        logger.info(f"    Rarity: {doc.get('rarity', 'N/A')}")
        logger.info(f"    Rating: {doc.get('rating', 'N/A')}")
        logger.info(f"    Tags: {', '.join(doc.get('tags', [])) if doc.get('tags') else 'なし'}")
        logger.info(f"    Source: {doc.get('source', 'unknown')}")
        logger.info(f"    URL: {doc.get('url', 'N/A')[:80]}...")
        
        # コンテンツのプレビュー（最初の300文字）
        if doc.get('content'):
            content_preview = doc['content'][:300].replace('\n', ' ')
            logger.info(f"    Content Preview:\n      {content_preview}...")
        else:
            logger.info(f"    Content: [No content]")
        
        logger.info(f"    " + "-"*76)
    
    # 統計情報
    logger.info("\n" + "="*80)
    logger.info("=== STATISTICS ===")
    logger.info("="*80)
    
    # 属性別集計
    element_counts = {}
    for doc in documents:
        elem = doc.get('element', 'Unknown')
        element_counts[elem] = element_counts.get(elem, 0) + 1
    
    logger.info("\n属性別キャラクター数:")
    for elem, count in sorted(element_counts.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {elem}: {count}件")
    
    # 評価点分布
    ratings = [doc.get('rating') for doc in documents if doc.get('rating')]
    if ratings:
        avg_rating = sum(ratings) / len(ratings)
        max_rating = max(ratings)
        min_rating = min(ratings)
        logger.info(f"\n評価点:")
        logger.info(f"  平均: {avg_rating:.2f}")
        logger.info(f"  最高: {max_rating}")
        logger.info(f"  最低: {min_rating}")
        logger.info(f"  評価あり: {len(ratings)}件 / {len(documents)}件")
    
    # タグ集計
    all_tags = []
    for doc in documents:
        if doc.get('tags'):
            all_tags.extend(doc['tags'])
    
    if all_tags:
        from collections import Counter
        tag_counts = Counter(all_tags)
        logger.info(f"\nよくあるタグ（上位10件）:")
        for tag, count in tag_counts.most_common(10):
            logger.info(f"  {tag}: {count}件")
    
    logger.info("\n" + "="*80)
    
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
