"""
グラブルWiki scraper - 用語集対応版
用語集は五十音順に分割されている（あ行、か行、さ行...）
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
import urllib.parse

from app.core.config import get_settings
from app.core.logging import setup_logging

logger = setup_logging()
settings = get_settings()


class WikiScraper:
    """Scraper for Wiki glossaries."""
    
    BASE_URL = "https://gbf-wiki.com"
    
    # 用語集の五十音順ページ
    TERM_PAGES = [
        "用語集/あ行",
        "用語集/か行", 
        "用語集/さ行",
        "用語集/た行",
        "用語集/な行",
        "用語集/は行",
        "用語集/ま行",
        "用語集/や行",
        "用語集/ら行",
        "用語集/わ行",
        "用語集/アルファベット、数字他",
    ]
    
    # 俗語集の五十音順ページ
    SLANG_PAGES = [
        "俗語集/あ行",
        "俗語集/か行",
        "俗語集/さ行",
        "俗語集/た行",
        "俗語集/な行",
        "俗語集/は行",
        "俗語集/ま行",
        "俗語集/や行",
        "俗語集/ら行",
        "俗語集/わ行",
        "俗語集/アルファベット、数字他",
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = settings.scraper_user_agent
    
    def _build_url(self, page_name: str) -> str:
        """Build URL for Wiki page."""
        encoded = urllib.parse.quote(page_name)
        return f"{self.BASE_URL}/index.php?{encoded}"
    
    def scrape_glossary_page(self, page_name: str, glossary_type: str) -> List[Dict[str, Any]]:
        """
        Scrape a single glossary page.
        
        Args:
            page_name: Page name (e.g., "用語集/あ行")
            glossary_type: "terms" or "slang"
        """
        url = self._build_url(page_name)
        logger.info(f"Scraping {page_name}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.encoding = 'utf-8'
            
            # lxmlでXPath使用
            import lxml.html
            tree = lxml.html.fromstring(response.content)
            
            # メインコンテンツ領域を取得（XPath: //table/tr/td[2]）
            content_elements = tree.xpath('//table/tr/td[2]')
            if not content_elements:
                logger.warning(f"Content not found for {page_name}")
                return []
            
            # BeautifulSoupで再パース
            html_str = lxml.html.tostring(content_elements[0], encoding='unicode')
            soup = BeautifulSoup(html_str, "lxml")
            
            items = []
            
            # h3/h4 + 次の要素（定義）のパターン
            for heading in soup.find_all(['h3', 'h4']):
                term = heading.get_text(strip=True)
                
                # †記号を除去
                term = term.replace('†', '').strip()
                
                # 次の段落/divを探す
                next_elem = heading.find_next_sibling(['p', 'div', 'ul'])
                if not next_elem:
                    continue
                
                definition = next_elem.get_text(strip=True)
                
                # フィルタリング
                if (term and definition and 
                    len(term) < 100 and 
                    len(definition) > 10 and
                    term not in ['↑', '関連ページ', '索引']):
                    
                    # コンテンツを整形
                    formatted_content = f"""【{term}】

{definition}

[分類: {glossary_type}]
[出典: グラブルWiki {page_name}]
""".strip()
                    
                    items.append({
                        "name": term,
                        "content": formatted_content,
                        "type": "glossary",
                        "glossary_type": glossary_type,
                        "source": "wiki",
                        "url": url,
                        "scraped_at": datetime.now(),
                    })
            
            logger.info(f"Found {len(items)} terms in {page_name}")
            return items
            
        except Exception as e:
            logger.error(f"Failed to scrape {page_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def scrape_all_glossaries(self, include_terms: bool = True, include_slang: bool = True) -> List[Dict[str, Any]]:
        """
        Scrape all glossary pages.
        
        Args:
            include_terms: Include 用語集
            include_slang: Include 俗語集
        """
        all_items = []
        
        # 用語集
        if include_terms:
            logger.info("=== Scraping 用語集 ===")
            for page in self.TERM_PAGES:
                try:
                    items = self.scrape_glossary_page(page, "terms")
                    all_items.extend(items)
                    time.sleep(settings.scraper_delay)
                except Exception as e:
                    logger.error(f"Error scraping {page}: {e}")
        
        # 俗語集
        if include_slang:
            logger.info("=== Scraping 俗語集 ===")
            for page in self.SLANG_PAGES:
                try:
                    items = self.scrape_glossary_page(page, "slang")
                    all_items.extend(items)
                    time.sleep(settings.scraper_delay)
                except Exception as e:
                    logger.error(f"Error scraping {page}: {e}")
        
        return all_items


async def scrape_wiki(
    character_limit: Optional[int] = None,
    include_glossaries: bool = True,
    include_terms: bool = True,
    include_slang: bool = True
) -> List[Dict[str, Any]]:
    """
    Scrape Wiki data (async wrapper).
    
    Args:
        character_limit: Not used (glossaries only for now)
        include_glossaries: Whether to include glossaries
        include_terms: Include 用語集
        include_slang: Include 俗語集
    """
    import concurrent.futures
    import asyncio
    
    def _scrape():
        if not include_glossaries:
            return []
        
        scraper = WikiScraper()
        return scraper.scrape_all_glossaries(
            include_terms=include_terms,
            include_slang=include_slang
        )
    
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, _scrape)


if __name__ == "__main__":
    import asyncio
    
    async def test():
        logger.info("Testing Wiki scraper...")
        
        # Test single page
        scraper = WikiScraper()
        logger.info("\n=== Testing single page ===")
        items = scraper.scrape_glossary_page("俗語集/あ行", "slang")
        logger.info(f"Found {len(items)} items")
        
        if items:
            for item in items[:3]:
                logger.info(f"\n{item['name']}:")
                logger.info(f"  {item['content'][:150]}...")
        
        # Test all glossaries
        logger.info("\n=== Testing all glossaries ===")
        all_items = await scrape_wiki(include_terms=False, include_slang=True)
        logger.info(f"\nTotal: {len(all_items)} glossary items")
    
    asyncio.run(test())

