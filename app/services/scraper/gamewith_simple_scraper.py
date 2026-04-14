"""
GameWith scraper using requests (no Playwright required).
シンプルで安定、MacOS/Windows両対応。
URLから直接キャラクター詳細を取得します。
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import re
import time
import requests
from bs4 import BeautifulSoup

from app.core.config import get_settings
from app.core.logging import setup_logging

logger = setup_logging()
settings = get_settings()


class GameWithSimpleScraper:
    """Simple scraper using requests (no Playwright)."""
    
    BASE_URL = "https://グランブルーファンタジー.gamewith.jp"
    CHARACTER_LIST_URL = "/article/show/20722"
    
    def __init__(self):
        """Initialize scraper."""
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.scraper_user_agent,
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        })
    
    def _fetch_page(self, url: str) -> str:
        """
        Fetch page content.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content
        """
        logger.info(f"Fetching: {url}")
        
        try:
            response = self.session.get(
                url,
                timeout=settings.scraper_timeout / 1000,  # ms to seconds
            )
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
            
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise
    
    def scrape_character_list(self) -> List[Dict[str, Any]]:
        """Scrape SSR character list from GameWith."""
        logger.info("Scraping character list from GameWith")
        
        url = f"{self.BASE_URL}{self.CHARACTER_LIST_URL}"
        content = self._fetch_page(url)
        soup = BeautifulSoup(content, "lxml")
        
        characters = []
        
        # キャラクターリストを取得
        char_list = soup.select_one("#GBFCharactorList")
        if not char_list:
            logger.error("Character list not found (#GBFCharactorList)")
            return []
        
        char_items = char_list.select("li")
        logger.info(f"Found {len(char_items)} character items")
        
        for item in char_items:
            try:
                # 属性を取得
                element = item.get("data-attr", "")
                
                # リンクを取得
                link = item.select_one("a")
                if not link:
                    continue
                
                char_url = link.get("href", "")
                if not char_url:
                    continue
                
                # キャラ名を取得
                name_elem = item.select_one("._n")
                if not name_elem:
                    continue
                
                name = name_elem.get_text(strip=True)
                
                # 評価点を取得
                rating_elem = item.select_one("._p")
                rating = None
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    try:
                        rating = float(rating_text)
                    except ValueError:
                        pass
                
                # タグを抽出
                tags = []
                
                if "add-new" in item.get("class", []):
                    tags.append("新キャラ")
                
                name_class = name_elem.get("class", [])
                tag_map = {
                    "is-limited": "リミテッド",
                    "is-summer": "水着/浴衣",
                    "is-halloween": "ハロウィン",
                    "is-xmas": "クリスマス",
                    "is-valentine": "バレンタイン",
                    "is-juten": "十天衆",
                    "is-sage": "十賢者",
                    "is-eto": "十二神将",
                    "is-collabo": "コラボ",
                    "is-free": "配布",
                }
                
                for class_name, tag_name in tag_map.items():
                    if class_name in name_class:
                        tags.append(tag_name)
                
                rel = name_elem.get("rel", "")
                if rel:
                    tags.append(rel)
                
                characters.append({
                    "name": name,
                    "element": element,
                    "rarity": "SSR",
                    "type": "character",
                    "url": char_url,
                    "rating": rating,
                    "tags": tags,
                    "source": "gamewith",
                })
                
            except Exception as e:
                logger.warning(f"Failed to parse character item: {e}")
                continue
        
        logger.info(f"Scraped {len(characters)} characters")
        return characters
    
    def scrape_character_detail(self, url: str) -> Dict[str, Any]:
        """
        Scrape detailed character information from URL.
        
        Args:
            url: Character page URL
            
        Returns:
            Character detail dictionary
        """
        logger.info(f"Scraping character detail: {url}")
        
        try:
            content = self._fetch_page(url)
            soup = BeautifulSoup(content, "lxml")
            
            # タイトルからキャラ名を取得
            title = soup.select_one("h1")
            name = title.get_text(strip=True) if title else "Unknown"
            
            # 記事本文を取得
            article = soup.select_one("article, .article-body, #article-body")
            
            if not article:
                logger.warning(f"Article content not found for {url}")
                return {
                    "url": url,
                    "content": "",
                    "scraped_at": datetime.now(),
                }
            
            # テキストコンテンツを抽出
            content_parts = []
            
            # 見出しとテキストを順番に抽出
            for elem in article.find_all(['h2', 'h3', 'h4', 'p', 'li', 'table']):
                if elem.name in ['h2', 'h3', 'h4']:
                    heading_text = elem.get_text(strip=True)
                    if heading_text and len(heading_text) < 100:  # 長すぎる見出しは除外
                        content_parts.append(f"\n## {heading_text}\n")
                elif elem.name == 'p':
                    text = elem.get_text(strip=True)
                    # 広告やノイズを除外
                    if text and len(text) > 10 and not text.startswith('PR'):
                        content_parts.append(text)
                elif elem.name == 'li':
                    text = elem.get_text(strip=True)
                    if text and len(text) > 5:
                        content_parts.append(f"- {text}")
                elif elem.name == 'table':
                    # テーブルは簡易的にテキスト化
                    rows = elem.find_all('tr')[:20]  # 最大20行
                    for row in rows:
                        cells = [td.get_text(strip=True) for td in row.find_all(['th', 'td'])]
                        if cells and any(cells):  # 空でない行のみ
                            content_parts.append(" | ".join(cells))
            
            full_content = "\n".join(content_parts)
            
            # 属性を抽出
            element = None
            for elem_name in ["火", "水", "土", "風", "光", "闇"]:
                if elem_name in full_content[:500]:
                    element = elem_name
                    break
            
            # タグ/カテゴリを抽出
            tags = []
            tag_keywords = {
                "初心者向け": ["初心者", "おすすめ", "序盤"],
                "高難易度": ["高難易度", "ソロ", "フルオート"],
                "周回": ["周回", "効率", "短期"],
                "サポート": ["サポート", "バフ", "デバフ", "支援"],
                "アタッカー": ["アタッカー", "火力", "ダメージ", "攻撃"],
                "回復": ["回復", "ヒール", "HP"],
                "防御": ["防御", "ダメカ", "カット"],
            }
            
            for tag, keywords in tag_keywords.items():
                if any(kw in full_content[:1000] for kw in keywords):
                    tags.append(tag)
            
            return {
                "name": name,
                "url": url,
                "content": full_content,
                "element": element,
                "tags": tags,
                "scraped_at": datetime.now(),
                "source": "gamewith",
            }
            
        except Exception as e:
            logger.error(f"Failed to scrape detail from {url}: {e}")
            return {
                "url": url,
                "content": "",
                "scraped_at": datetime.now(),
            }
    
    def scrape_all_characters(self, limit: Optional[int] = None, fetch_details: bool = True) -> List[Dict[str, Any]]:
        """
        Scrape all character information.
        
        Args:
            limit: Limit number of characters
            fetch_details: If True, fetch detailed info from each character page
        """
        import time
        
        # Get character list
        characters = self.scrape_character_list()
        
        if limit:
            characters = characters[:limit]
        
        logger.info(f"Processing {len(characters)} characters (fetch_details={fetch_details})")
        
        if not fetch_details:
            # 詳細取得しない場合はリスト情報のみ
            logger.info("Skipping detail pages - using list info only")
            return characters
        
        # 詳細ページを取得
        all_details = []
        
        for i, char in enumerate(characters):
            if not char.get("url"):
                logger.warning(f"No URL for character: {char.get('name')}")
                all_details.append(char)
                continue
            
            try:
                logger.info(f"[{i+1}/{len(characters)}] Fetching details: {char.get('name')}")
                
                detail = self.scrape_character_detail(char["url"])
                
                # Merge list info with detail
                merged = {**char, **detail}
                
                # 詳細から取得したタグを追加
                if detail.get("tags"):
                    existing_tags = set(merged.get("tags", []))
                    new_tags = set(detail["tags"])
                    merged["tags"] = list(existing_tags | new_tags)
                
                all_details.append(merged)
                
                # Rate limiting（サーバーに優しく）
                time.sleep(settings.scraper_delay)
                
            except Exception as e:
                logger.error(f"Failed to scrape {char.get('name')}: {e}")
                # エラーでもリスト情報は保存
                all_details.append(char)
                continue
        
        return all_details


def scrape_gamewith_simple(character_limit: Optional[int] = 10, fetch_details: bool = True) -> List[Dict[str, Any]]:
    """
    Scrape GameWith data (synchronous version).
    
    Args:
        character_limit: Limit number of characters
        fetch_details: If True, fetch detailed info from each character page
        
    Returns:
        List of scraped documents
    """
    scraper = GameWithSimpleScraper()
    return scraper.scrape_all_characters(limit=character_limit, fetch_details=fetch_details)


# Async wrapper for compatibility
async def scrape_gamewith(character_limit: Optional[int] = 10, fetch_details: bool = True) -> List[Dict[str, Any]]:
    """
    Scrape GameWith data (async wrapper).
    
    Args:
        character_limit: Limit number of characters
        fetch_details: If True, fetch detailed info from each character page
    """
    # Run in thread pool to avoid blocking
    import concurrent.futures
    
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool,
            lambda: scrape_gamewith_simple(character_limit, fetch_details)
        )
    
    return result


if __name__ == "__main__":
    logger.info("Testing GameWith simple scraper...")
    
    try:
        # テスト: 詳細取得あり
        logger.info("=== Test with details ===")
        data = scrape_gamewith_simple(character_limit=2, fetch_details=True)
        logger.info(f"Scraped {len(data)} items with details")
        for item in data:
            logger.info(f"\n  Name: {item['name']}")
            logger.info(f"  Element: {item['element']}")
            logger.info(f"  Rating: {item.get('rating', 'N/A')}")
            logger.info(f"  Tags: {item.get('tags', [])}")
            logger.info(f"  Content length: {len(item.get('content', ''))} chars")
            logger.info(f"  Content preview: {item.get('content', '')[:200]}...")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
