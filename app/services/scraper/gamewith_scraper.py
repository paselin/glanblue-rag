"""
GameWith scraper for Granblue Fantasy - REAL IMPLEMENTATION
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import re

try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    
from bs4 import BeautifulSoup

from app.core.config import get_settings
from app.core.logging import setup_logging

logger = setup_logging()
settings = get_settings()


class GameWithScraper:
    """Scraper for GameWith Granblue Fantasy section."""
    
    BASE_URL = "https://gamewith.jp/granblue"
    
    # キャラクター一覧ページ
    CHARACTER_LIST_URL = "/article/show/20722"
    
    def __init__(self):
        """Initialize scraper."""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright is not installed. "
                "Install with: pip install playwright && playwright install chromium"
            )
        
        self.settings = settings
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    async def __aenter__(self):
        """Context manager entry."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def _fetch_page(self, url: str) -> str:
        """Fetch page content."""
        if not self.browser:
            raise RuntimeError("Browser not initialized.")
        
        page = await self.browser.new_page()
        
        try:
            logger.info(f"Fetching: {url}")
            await page.goto(url, timeout=settings.scraper_timeout)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)  # 追加待機
            
            content = await page.content()
            return content
            
        finally:
            await page.close()
    
    async def scrape_character_list(self) -> List[Dict[str, Any]]:
        """
        Scrape SSR character list from GameWith.
        
        HTML Structure:
        <ol id="GBFCharactorList">
          <li data-attr="水" data-kana="...">
            <a href="...">
              <div class="_c">画像</div>
              <div class="_b">
                <div class="_n">キャラ名</div>
                <div class="_d">詳細情報</div>
              </div>
              <div class="_p">評価点</div>
            </a>
          </li>
        </ol>
        """
        logger.info("Scraping character list from GameWith")
        
        url = f"{self.BASE_URL}{self.CHARACTER_LIST_URL}"
        content = await self._fetch_page(url)
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
                
                # タグを抽出（リミテッド、水着など）
                tags = []
                
                # NEWタグ
                if "add-new" in item.get("class", []):
                    tags.append("新キャラ")
                
                # 特殊タグ（リミテッド、水着など）
                name_class = name_elem.get("class", [])
                if "is-limited" in name_class:
                    tags.append("リミテッド")
                if "is-summer" in name_class:
                    tags.append("水着/浴衣")
                if "is-halloween" in name_class:
                    tags.append("ハロウィン")
                if "is-xmas" in name_class:
                    tags.append("クリスマス")
                if "is-valentine" in name_class:
                    tags.append("バレンタイン")
                if "is-juten" in name_class:
                    tags.append("十天衆")
                if "is-sage" in name_class:
                    tags.append("十賢者")
                if "is-eto" in name_class:
                    tags.append("十二神将")
                if "is-collabo" in name_class:
                    tags.append("コラボ")
                if "is-free" in name_class:
                    tags.append("配布")
                
                # rel属性からもタグ取得
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
    
    async def scrape_character_detail(self, url: str) -> Dict[str, Any]:
        """
        Scrape detailed character information.
        """
        logger.info(f"Scraping character detail: {url}")
        
        content = await self._fetch_page(url)
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
                if heading_text:
                    content_parts.append(f"\n## {heading_text}\n")
            elif elem.name == 'p':
                text = elem.get_text(strip=True)
                if text and len(text) > 10:  # 短すぎるテキストは除外
                    content_parts.append(text)
            elif elem.name == 'li':
                text = elem.get_text(strip=True)
                if text:
                    content_parts.append(f"- {text}")
            elif elem.name == 'table':
                # テーブルは簡易的にテキスト化
                rows = elem.find_all('tr')[:10]  # 最初の10行のみ
                for row in rows:
                    cells = [td.get_text(strip=True) for td in row.find_all(['th', 'td'])]
                    if cells:
                        content_parts.append(" | ".join(cells))
        
        full_content = "\n".join(content_parts)
        
        # 属性を抽出
        element = None
        for elem_name in ["火", "水", "土", "風", "光", "闇"]:
            if elem_name in full_content[:500]:
                element = elem_name
                break
        
        return {
            "name": name,
            "url": url,
            "content": full_content,
            "element": element,
            "scraped_at": datetime.now(),
            "source": "gamewith",
        }
    
    async def scrape_all_characters(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape all character information."""
        # Get character list
        characters = await self.scrape_character_list()
        
        if limit:
            characters = characters[:limit]
        
        all_details = []
        
        # Scrape each character with delay
        for i, char in enumerate(characters):
            if not char.get("url"):
                logger.warning(f"No URL for character: {char.get('name')}")
                all_details.append(char)  # リストの情報だけでも保存
                continue
            
            try:
                logger.info(f"Scraping character {i+1}/{len(characters)}: {char.get('name')}")
                
                detail = await self.scrape_character_detail(char["url"])
                
                # Merge list info with detail
                merged = {**char, **detail}
                all_details.append(merged)
                
                # Rate limiting
                await asyncio.sleep(settings.scraper_delay)
                
            except Exception as e:
                logger.error(f"Failed to scrape {char.get('name')}: {e}")
                # エラーでもリスト情報は保存
                all_details.append(char)
                continue
        
        return all_details


async def scrape_gamewith(character_limit: Optional[int] = 10) -> List[Dict[str, Any]]:
    """
    Scrape GameWith data.
    """
    async with GameWithScraper() as scraper:
        return await scraper.scrape_all_characters(limit=character_limit)


if __name__ == "__main__":
    async def main():
        logger.info("Testing GameWith scraper...")
        
        try:
            data = await scrape_gamewith(character_limit=3)
            logger.info(f"Scraped {len(data)} items")
            for item in data:
                logger.info(f"  - {item['name']} ({item['element']}) Rating: {item.get('rating', 'N/A')}")
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    asyncio.run(main())
    
    def __init__(self):
        """Initialize scraper."""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright is not installed. "
                "Install with: pip install playwright && playwright install chromium"
            )
        
        self.settings = settings
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    async def __aenter__(self):
        """Context manager entry."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def _fetch_page(self, url: str) -> str:
        """
        Fetch page content.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized.")
        
        page = await self.browser.new_page()
        
        try:
            logger.info(f"Fetching: {url}")
            await page.goto(url, timeout=settings.scraper_timeout)
            await page.wait_for_load_state("networkidle")
            
            content = await page.content()
            return content
            
        finally:
            await page.close()
    
    async def scrape_character_list(self) -> List[Dict[str, Any]]:
        """
        Scrape character list from GameWith.
        
        GameWithの実際のHTML構造に合わせて調整が必要です。
        
        Returns:
            List of character data dictionaries
        """
        logger.info("Scraping character list from GameWith")
        
        characters = []
        
        # 複数のURL候補を試す
        for url_path in self.CHARACTER_LIST_URLS:
            try:
                url = f"{self.BASE_URL}{url_path}"
                content = await self._fetch_page(url)
                soup = BeautifulSoup(content, "lxml")
                
                # デバッグ: ページタイトルを確認
                title = soup.select_one("h1, title")
                logger.info(f"Page title: {title.get_text(strip=True) if title else 'N/A'}")
                
                # 様々なセレクタパターンを試す
                selectors = [
                    "article.character-card",
                    ".character-list-item",
                    ".card.character",
                    "div[class*='character']",
                    "li.list-item",
                    "table.character-table tr",
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    if elements:
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        
                        # サンプルを表示
                        if elements:
                            sample = elements[0]
                            logger.debug(f"Sample element HTML:\n{sample.prettify()[:500]}")
                        
                        # ここで実際のHTML構造に合わせてパース
                        # TODO: GameWithの実際の構造を確認して実装
                        
                        break
                
                if not elements:
                    logger.warning(f"No character elements found on {url}")
                    # 全HTML構造をログに出力（デバッグ用）
                    logger.debug(f"Page structure:\n{soup.prettify()[:2000]}")
                
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
                continue
        
        if not characters:
            logger.warning("No characters found. GameWithの構造が変わった可能性があります。")
            logger.warning("手動でページを確認し、セレクタを更新してください。")
        
        return characters
    
    async def scrape_character_detail(self, url: str) -> Dict[str, Any]:
        """Scrape character detail (placeholder)."""
        logger.warning("Character detail scraping not yet implemented")
        return {
            "url": url,
            "content": "",
            "scraped_at": datetime.now(),
        }
    
    async def scrape_party_compositions(self) -> List[Dict[str, Any]]:
        """Scrape party compositions (placeholder)."""
        logger.warning("Party composition scraping not yet implemented")
        return []
    
    async def scrape_all_characters(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape all characters."""
        characters = await self.scrape_character_list()
        
        if limit:
            characters = characters[:limit]
        
        return characters


async def scrape_gamewith(character_limit: Optional[int] = 10) -> List[Dict[str, Any]]:
    """
    Scrape GameWith data.
    
    現在は実装途中です。GameWithの実際のHTML構造を確認してください。
    """
    logger.warning("GameWith scraper is under development.")
    logger.warning("Actual HTML structure needs to be verified and implemented.")
    
    # 暫定: 空リストを返す
    return []


if __name__ == "__main__":
    async def main():
        logger.info("Testing GameWith scraper...")
        
        try:
            async with GameWithScraper() as scraper:
                chars = await scraper.scrape_character_list()
                logger.info(f"Result: {len(chars)} characters")
        except ImportError as e:
            logger.error(f"Playwright not available: {e}")
            logger.error("Install with: pip install playwright && playwright install chromium")
        except Exception as e:
            logger.error(f"Error: {e}")
    
    asyncio.run(main())
    
    def __init__(self):
        """Initialize scraper."""
        self.settings = settings
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    async def __aenter__(self):
        """Context manager entry."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def scrape_character_list(self) -> List[Dict[str, Any]]:
        """
        Scrape SSR character list from GameWith.
        
        Returns:
            List of character data dictionaries
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use 'async with' context manager.")
        
        logger.info("Scraping SSR character list from GameWith")
        
        page = await self.browser.new_page()
        
        try:
            # SSRキャラ一覧ページ
            url = f"{self.BASE_URL}{self.PRIORITY_PAGES['character_list']}"
            await page.goto(url, timeout=settings.scraper_timeout)
            await page.wait_for_load_state("networkidle")
            
            # ページ内容を取得
            content = await page.content()
            soup = BeautifulSoup(content, "lxml")
            
            characters = []
            
            # GameWithの構造: キャラクターカードを探す
            # 実際のHTML構造に応じて調整が必要
            char_cards = soup.select(".gw-character-card, .character-list-item, article.character")
            
            logger.info(f"Found {len(char_cards)} character elements")
            
            for card in char_cards:
                try:
                    # キャラ名を抽出
                    name_elem = card.select_one(".name, .character-name, h3, h4")
                    if not name_elem:
                        continue
                    
                    name = name_elem.get_text(strip=True)
                    
                    # 属性を抽出（火、水、土、風、光、闇）
                    element = None
                    element_elem = card.select_one(".element, .attr, [class*='element'], [class*='attr']")
                    if element_elem:
                        element_text = element_elem.get_text(strip=True)
                        for elem in ["火", "水", "土", "風", "光", "闇"]:
                            if elem in element_text:
                                element = elem
                                break
                    
                    # キャラページのURL
                    link_elem = card.select_one("a[href*='/article/show/']")
                    char_url = None
                    if link_elem and link_elem.get("href"):
                        href = link_elem["href"]
                        if href.startswith("/"):
                            char_url = f"https://gamewith.jp{href}"
                        else:
                            char_url = href
                    
                    # 評価点数
                    rating = None
                    rating_elem = card.select_one(".rating, .score, .point")
                    if rating_elem:
                        rating_text = rating_elem.get_text(strip=True)
                        # "9.5点" などから数値を抽出
                        match = re.search(r'(\d+\.?\d*)', rating_text)
                        if match:
                            rating = float(match.group(1))
                    
                    characters.append({
                        "name": name,
                        "element": element,
                        "rarity": "SSR",
                        "type": "character",
                        "url": char_url,
                        "rating": rating,
                        "source": "gamewith",
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to parse character card: {e}")
                    continue
            
            logger.info(f"Scraped {len(characters)} characters from GameWith")
            return characters
            
        except Exception as e:
            logger.error(f"Failed to scrape character list: {e}")
            raise
        finally:
            await page.close()
    
    async def scrape_character_detail(self, url: str) -> Dict[str, Any]:
        """
        Scrape detailed character information.
        
        Args:
            url: Character page URL
            
        Returns:
            Character detail dictionary
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized.")
        
        logger.info(f"Scraping character detail: {url}")
        
        page = await self.browser.new_page()
        
        try:
            await page.goto(url, timeout=settings.scraper_timeout)
            await page.wait_for_load_state("networkidle")
            
            content = await page.content()
            soup = BeautifulSoup(content, "lxml")
            
            # タイトルからキャラ名を取得
            title = soup.select_one("h1, .article-title")
            name = title.get_text(strip=True) if title else "Unknown"
            
            # 本文を取得
            article_body = soup.select_one(".article-body, .content-body, main article")
            
            if not article_body:
                logger.warning(f"Could not find article body for {url}")
                return {"url": url, "content": "", "scraped_at": datetime.now()}
            
            # テキストコンテンツを抽出
            content_parts = []
            
            # 見出しとテキストを順番に抽出
            for elem in article_body.find_all(['h2', 'h3', 'h4', 'p', 'ul', 'table']):
                if elem.name in ['h2', 'h3', 'h4']:
                    content_parts.append(f"\n## {elem.get_text(strip=True)}\n")
                elif elem.name == 'p':
                    text = elem.get_text(strip=True)
                    if text:
                        content_parts.append(text)
                elif elem.name == 'ul':
                    for li in elem.find_all('li'):
                        content_parts.append(f"- {li.get_text(strip=True)}")
                elif elem.name == 'table':
                    # テーブルは簡易的にテキスト化
                    for row in elem.find_all('tr'):
                        cells = [td.get_text(strip=True) for td in row.find_all(['th', 'td'])]
                        content_parts.append(" | ".join(cells))
            
            full_content = "\n".join(content_parts)
            
            # 属性を抽出
            element = None
            for elem_name in ["火", "水", "土", "風", "光", "闇"]:
                if elem_name in full_content[:500]:  # 冒頭部分から
                    element = elem_name
                    break
            
            # タグ/カテゴリを抽出
            tags = []
            tag_keywords = {
                "初心者向け": ["初心者", "おすすめ", "序盤"],
                "高難易度": ["高難易度", "ソロ", "フルオート"],
                "周回": ["周回", "効率", "短期"],
                "サポート": ["サポート", "バフ", "デバフ"],
                "アタッカー": ["アタッカー", "火力", "ダメージ"],
            }
            
            for tag, keywords in tag_keywords.items():
                if any(kw in full_content for kw in keywords):
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
            logger.error(f"Failed to scrape character detail from {url}: {e}")
            raise
        finally:
            await page.close()
    
    async def scrape_party_compositions(self) -> List[Dict[str, Any]]:
        """
        Scrape party composition guides.
        
        Returns:
            List of party composition data
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized.")
        
        logger.info("Scraping party compositions from GameWith")
        
        page = await self.browser.new_page()
        
        try:
            url = f"{self.BASE_URL}{self.PRIORITY_PAGES['party_guide']}"
            await page.goto(url, timeout=settings.scraper_timeout)
            await page.wait_for_load_state("networkidle")
            
            content = await page.content()
            soup = BeautifulSoup(content, "lxml")
            
            compositions = []
            
            # 編成ガイドのセクションを抽出
            sections = soup.select(".party-section, section")
            
            for section in sections:
                try:
                    # セクションタイトル
                    title_elem = section.select_one("h2, h3, .section-title")
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # 本文
                    content_text = section.get_text(strip=True)
                    
                    # 属性を判定
                    element = None
                    for elem_name in ["火", "水", "土", "風", "光", "闇"]:
                        if elem_name in title or elem_name in content_text[:100]:
                            element = elem_name
                            break
                    
                    compositions.append({
                        "name": title,
                        "type": "party_composition",
                        "content": content_text,
                        "element": element,
                        "url": url,
                        "source": "gamewith",
                        "scraped_at": datetime.now(),
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to parse party section: {e}")
                    continue
            
            logger.info(f"Scraped {len(compositions)} party compositions")
            return compositions
            
        except Exception as e:
            logger.error(f"Failed to scrape party compositions: {e}")
            raise
        finally:
            await page.close()
    
    async def scrape_all_characters(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Scrape all character information.
        
        Args:
            limit: Maximum number of characters to scrape (None for all)
            
        Returns:
            List of character details
        """
        # Get character list
        characters = await self.scrape_character_list()
        
        if limit:
            characters = characters[:limit]
        
        all_details = []
        
        # Scrape each character with delay
        for i, char in enumerate(characters):
            if not char.get("url"):
                logger.warning(f"No URL for character: {char.get('name')}")
                continue
            
            try:
                logger.info(f"Scraping character {i+1}/{len(characters)}: {char.get('name')}")
                
                detail = await self.scrape_character_detail(char["url"])
                
                # Merge list info with detail
                merged = {**char, **detail}
                all_details.append(merged)
                
                # Rate limiting
                await asyncio.sleep(settings.scraper_delay)
                
            except Exception as e:
                logger.error(f"Failed to scrape {char.get('name')}: {e}")
                continue
        
        return all_details


async def scrape_gamewith(character_limit: Optional[int] = 10) -> List[Dict[str, Any]]:
    """
    Scrape GameWith data.
    
    Args:
        character_limit: Limit number of characters (None for all)
        
    Returns:
        List of scraped documents
    """
    async with GameWithScraper() as scraper:
        # キャラクター情報を取得
        characters = await scraper.scrape_all_characters(limit=character_limit)
        
        # 編成情報を取得
        try:
            compositions = await scraper.scrape_party_compositions()
            characters.extend(compositions)
        except Exception as e:
            logger.error(f"Failed to scrape compositions: {e}")
        
        return characters


if __name__ == "__main__":
    # Test scraper
    async def main():
        logger.info("Starting GameWith scraper test...")
        data = await scrape_gamewith(character_limit=3)  # テストは3件のみ
        logger.info(f"Scraped {len(data)} items")
        for item in data:
            logger.info(f"  - {item.get('name', 'N/A')} ({item.get('type', 'unknown')})")
    
    asyncio.run(main())
