"""
Simple GameWith HTML fetcher (without Playwright).
curlやrequestsでHTMLを取得して分析します。
"""
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.logging import setup_logging

logger = setup_logging()


def analyze_gamewith_simple():
    """GameWithのHTML構造を分析（シンプル版）"""
    
    urls = {
        "character_list": "https://xn--bck3aza1a2if6kra4ee0hf.gamewith.jp/article/show/20722",
        "character_detail": "https://xn--bck3aza1a2if6kra4ee0hf.gamewith.jp/article/show/547954",  # カタリナ
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    for name, url in urls.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Analyzing: {name}")
        logger.info(f"URL: {url}")
        logger.info(f"{'='*60}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "lxml")
            
            # ページタイトル
            title = soup.select_one("h1, .article-title, title")
            logger.info(f"Title: {title.get_text(strip=True) if title else 'N/A'}")
            
            # 主要な構造要素を探す
            logger.info("\n--- Analyzing structure ---")
            
            # 様々なパターンを試す
            patterns = [
                ("table rows", "table tr"),
                ("list items", "li"),
                ("article elements", "article"),
                ("divs with card class", "div.card, div[class*='card']"),
                ("divs with character class", "div[class*='character'], div[class*='chara']"),
                ("divs with ranking class", "div[class*='ranking'], div[class*='rank']"),
                ("all links", "a[href*='/article/show/']"),
            ]
            
            for pattern_name, selector in patterns:
                elements = soup.select(selector)
                count = len(elements)
                logger.info(f"{pattern_name} ({selector}): {count} found")
                
                if elements and count >= 3:
                    logger.info(f"\n  Sample elements (first 3):")
                    for idx, elem in enumerate(elements[:3]):
                        logger.info(f"  [{idx+1}] Classes: {elem.get('class', [])}")
                        text = elem.get_text(strip=True)[:80]
                        logger.info(f"      Text: {text}")
                        
                        # リンクを探す
                        link = elem.find("a")
                        if link and link.get('href'):
                            logger.info(f"      Link: {link.get('href')}")
                    
                    # 最初の要素の詳細構造
                    if count > 5:  # リストらしい
                        logger.info(f"\n  Detailed structure of first element:")
                        sample = elements[0]
                        logger.info(sample.prettify()[:600])
            
            # メインコンテンツエリアを探す
            logger.info("\n--- Looking for main content area ---")
            main_selectors = [
                "article",
                ".article-body",
                ".content",
                "main",
                "#content",
                ".main-content"
            ]
            
            for selector in main_selectors:
                main = soup.select_one(selector)
                if main:
                    logger.info(f"Found main content: {selector}")
                    # 見出しを取得
                    headings = main.find_all(['h2', 'h3'])[:5]
                    if headings:
                        logger.info("  Headings:")
                        for h in headings:
                            logger.info(f"    - {h.get_text(strip=True)}")
                    break
            
            # Save HTML for inspection
            output_file = f"gamewith_{name}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            logger.info(f"\nFull HTML saved to: {output_file}")
            
        except Exception as e:
            logger.error(f"Error analyzing {name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    logger.info("\n" + "="*60)
    logger.info("Analysis complete!")
    logger.info("Check the generated HTML files:")
    logger.info("  - gamewith_character_list.html")
    logger.info("  - gamewith_character_ranking.html")
    logger.info("="*60)


if __name__ == "__main__":
    logger.info("GameWith Structure Analyzer (Simple version)")
    logger.info("This tool will fetch GameWith HTML and analyze structure\n")
    
    analyze_gamewith_simple()
