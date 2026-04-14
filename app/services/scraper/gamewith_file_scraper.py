"""
GameWith scraper using local HTML files.
既に取得したHTMLファイルからデータを抽出します。
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import re

from app.core.logging import setup_logging

logger = setup_logging()


def scrape_from_html_file(
    html_file: str = "gamewith_character_list.html"
) -> List[Dict[str, Any]]:
    """
    Parse GameWith HTML file.
    
    Args:
        html_file: Path to HTML file
        
    Returns:
        List of character data
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logger.error("BeautifulSoup not installed. Install with: pip install beautifulsoup4 lxml")
        raise
    
    logger.info(f"Parsing HTML file: {html_file}")
    
    html_path = Path(html_file)
    if not html_path.exists():
        logger.error(f"HTML file not found: {html_file}")
        return []
    
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    
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
            # 属性
            element = item.get("data-attr", "")
            
            # リンク
            link = item.select_one("a")
            if not link:
                continue
            
            char_url = link.get("href", "")
            
            # キャラ名
            name_elem = item.select_one("._n")
            if not name_elem:
                continue
            
            name = name_elem.get_text(strip=True)
            
            # 評価点
            rating_elem = item.select_one("._p")
            rating = None
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                try:
                    rating = float(rating_text)
                except ValueError:
                    pass
            
            # タグ
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
            
            # 詳細情報の簡易版（一覧ページから）
            detail_elem = item.select_one("._d")
            detail_text = detail_elem.get_text(strip=True) if detail_elem else ""
            
            # 簡易コンテンツ作成
            content = f"""
{name}（SSR・{element}属性）

【評価点】
{rating if rating else '未評価'}/10点

【特徴】
{detail_text if detail_text else '詳細情報は個別ページを参照'}

【タグ】
{', '.join(tags) if tags else 'なし'}

【情報源】
GameWith SSRキャラ評価一覧
URL: {char_url}
"""
            
            characters.append({
                "id": f"gamewith_char_{name.replace(' ', '_')}",
                "name": name,
                "element": element,
                "rarity": "SSR",
                "type": "character",
                "url": char_url,
                "rating": rating,
                "tags": tags,
                "content": content.strip(),
                "source": "gamewith",
                "scraped_at": datetime.now(),
            })
            
        except Exception as e:
            logger.warning(f"Failed to parse character item: {e}")
            continue
    
    logger.info(f"Parsed {len(characters)} characters from HTML file")
    return characters


async def scrape_gamewith_from_file(
    character_limit: Optional[int] = None,
    html_file: str = "gamewith_character_list.html"
) -> List[Dict[str, Any]]:
    """
    Async wrapper for file-based scraping.
    """
    characters = scrape_from_html_file(html_file)
    
    if character_limit:
        characters = characters[:character_limit]
    
    return characters


if __name__ == "__main__":
    logger.info("Testing HTML file scraper...")
    
    try:
        data = scrape_from_html_file()
        logger.info(f"\nParsed {len(data)} items")
        
        # 最初の10件を表示
        logger.info("\nFirst 10 characters:")
        for i, item in enumerate(data[:10]):
            logger.info(f"{i+1}. {item['name']} ({item['element']}) Rating: {item.get('rating', 'N/A')} Tags: {item.get('tags', [])}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
