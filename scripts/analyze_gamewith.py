"""
GameWith HTML structure analyzer.
実際のGameWithページの構造を分析するツール。
"""
import sys
from pathlib import Path
import asyncio

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from app.core.logging import setup_logging

logger = setup_logging()


async def analyze_gamewith_structure():
    """GameWithのHTML構造を分析"""
    
    urls = {
        "character_list": "https://gamewith.jp/granblue/article/show/20722",
        "character_ranking": "https://gamewith.jp/granblue/article/show/21496",
        "character_detail": "https://gamewith.jp/granblue/article/show/21222",  # カタリナ
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False で見える
        page = await browser.new_page()
        
        for name, url in urls.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Analyzing: {name}")
            logger.info(f"URL: {url}")
            logger.info(f"{'='*60}")
            
            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("networkidle")
                
                # Wait a bit for dynamic content
                await asyncio.sleep(3)
                
                content = await page.content()
                soup = BeautifulSoup(content, "lxml")
                
                # ページタイトル
                title = soup.select_one("h1, .article-title, title")
                logger.info(f"Title: {title.get_text(strip=True) if title else 'N/A'}")
                
                # 主要な構造要素を探す
                logger.info("\n--- Analyzing structure ---")
                
                # キャラクター一覧の場合
                if "list" in name or "ranking" in name:
                    logger.info("\n*** Looking for character cards/items ***")
                    
                    # 様々なパターンを試す
                    patterns = [
                        ("table rows", "table tr"),
                        ("list items", "li"),
                        ("article elements", "article"),
                        ("card divs", "div.card, div[class*='card']"),
                        ("character divs", "div[class*='character'], div[class*='chara']"),
                        ("ranking items", "div[class*='ranking'], div[class*='rank']"),
                    ]
                    
                    for pattern_name, selector in patterns:
                        elements = soup.select(selector)
                        logger.info(f"{pattern_name} ({selector}): {len(elements)} found")
                        
                        if elements and len(elements) > 5:
                            logger.info(f"\n  Sample element (first one):")
                            sample = elements[0]
                            logger.info(f"  Classes: {sample.get('class', [])}")
                            logger.info(f"  Text preview: {sample.get_text(strip=True)[:100]}")
                            
                            # リンクを探す
                            links = sample.find_all("a")
                            if links:
                                logger.info(f"  Links found: {len(links)}")
                                logger.info(f"  First link: {links[0].get('href')}")
                            
                            # 画像を探す
                            imgs = sample.find_all("img")
                            if imgs:
                                logger.info(f"  Images found: {len(imgs)}")
                                logger.info(f"  First img alt: {imgs[0].get('alt', 'N/A')}")
                            
                            logger.info(f"\n  HTML structure:")
                            logger.info(sample.prettify()[:500])
                
                # キャラクター詳細の場合
                elif "detail" in name:
                    logger.info("\n*** Analyzing character detail page ***")
                    
                    # メインコンテンツ
                    main_content = soup.select_one("article, .article-body, .content, main")
                    if main_content:
                        logger.info("Main content found")
                        
                        # 見出しを取得
                        headings = main_content.find_all(['h2', 'h3', 'h4'])
                        logger.info(f"\nHeadings found: {len(headings)}")
                        for i, h in enumerate(headings[:5]):
                            logger.info(f"  {i+1}. {h.name}: {h.get_text(strip=True)}")
                        
                        # テーブルを探す
                        tables = main_content.find_all("table")
                        logger.info(f"\nTables found: {len(tables)}")
                        if tables:
                            logger.info(f"  First table preview:")
                            rows = tables[0].find_all("tr")[:3]
                            for row in rows:
                                cells = [td.get_text(strip=True) for td in row.find_all(['th', 'td'])]
                                logger.info(f"    {' | '.join(cells)}")
                
                # Save HTML for inspection
                output_file = f"gamewith_{name}.html"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(soup.prettify())
                logger.info(f"\nFull HTML saved to: {output_file}")
                
            except Exception as e:
                logger.error(f"Error analyzing {name}: {e}")
        
        logger.info("\n" + "="*60)
        logger.info("Analysis complete. Check the generated HTML files.")
        logger.info("="*60)
        
        # ブラウザを開いたままにして手動で確認できるようにする
        logger.info("\nBrowser window left open for manual inspection.")
        logger.info("Press Ctrl+C to close.")
        
        try:
            await asyncio.sleep(300)  # 5分待機
        except KeyboardInterrupt:
            logger.info("Closing browser...")
        
        await browser.close()


if __name__ == "__main__":
    logger.info("GameWith Structure Analyzer")
    logger.info("This tool will:")
    logger.info("1. Open GameWith pages in a browser")
    logger.info("2. Analyze HTML structure")
    logger.info("3. Save HTML files for inspection")
    logger.info("\nStarting in 3 seconds...")
    
    asyncio.run(analyze_gamewith_structure())
