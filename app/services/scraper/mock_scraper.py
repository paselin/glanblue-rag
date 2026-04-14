"""
Simple mock scraper for testing.
実際のGameWithスクレイピングの代わりに、ダミーデータを返します。
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import random

from app.core.logging import setup_logging

logger = setup_logging()


# モックデータ
MOCK_CHARACTERS = [
    {
        "name": "ベリアル",
        "element": "闇",
        "rarity": "SSR",
        "type": "character",
        "rating": 9.8,
        "content": """
ベリアル（SSR・闇属性）

【評価】
闇属性最強クラスのサポートキャラ。全体攻撃UP、防御DOWN、奥義ゲージUPなど多彩なサポート能力を持つ。

【アビリティ】
1. ムーンライス・ティロフィナーレ
   - 敵全体に闇属性ダメージ
   - 全体の攻撃UP、防御DOWN付与

2. ユー・アー・マイ・ヴァンプ
   - 味方全体の奥義ゲージUP
   - 確定トリプルアタック付与

【おすすめ編成】
- 高難易度クエスト全般
- フルオートでも活躍
- サポーターとして必須級

【入手方法】
期間限定ガチャ
""",
        "tags": ["高難易度", "サポート", "必須級"],
        "source": "gamewith_mock",
        "url": "https://gamewith.jp/granblue/article/show/mock1"
    },
    {
        "name": "サンダルフォン",
        "element": "光",
        "rarity": "SSR",
        "type": "character",
        "rating": 9.5,
        "content": """
サンダルフォン（SSR・光属性）

【評価】
光属性トップクラスのアタッカー兼サポーター。高火力と味方強化を両立。

【アビリティ】
1. パラダイス・ロスト
   - 敵に光属性ダメージ（特大）
   - 自分の奥義ゲージUP

2. ソル・アンド・シャドウ
   - 味方全体の光属性攻撃UP
   - 回復効果付与

【おすすめ編成】
- ルシファーHL
- 高難易度光属性クエスト
- フルオート周回

【入手方法】
期間限定ガチャ
""",
        "tags": ["光属性", "アタッカー", "高難易度"],
        "source": "gamewith_mock",
        "url": "https://gamewith.jp/granblue/article/show/mock2"
    },
    {
        "name": "ノイシュ",
        "element": "土",
        "rarity": "SSR",
        "type": "character",
        "rating": 8.5,
        "content": """
ノイシュ（SSR・土属性）

【評価】
土属性の防御・サポートに特化したキャラ。ダメージカットと回復で安定した戦闘が可能。

【アビリティ】
1. アンブレイカブル
   - 味方全体にダメージカット（70%/1回）
   - かばう効果付与

2. リザレクション
   - 味方単体のHP回復
   - 弱体効果1つ回復

【おすすめ編成】
- 高難易度ソロ攻略
- 長期戦
- 初心者の安定要員

【入手方法】
サプライズチケット交換可能
""",
        "tags": ["土属性", "防御", "初心者向け"],
        "source": "gamewith_mock",
        "url": "https://gamewith.jp/granblue/article/show/mock3"
    },
]

MOCK_COMPOSITIONS = [
    {
        "name": "火属性高難易度編成",
        "type": "party_composition",
        "element": "火",
        "content": """
火属性高難易度編成ガイド

【推奨編成】
メイン: アラナン
サブ1: アテナ
サブ2: ミカエル
サブ3: エッセル

【武器編成】
メイン: イクサバ
サブ: コロ杖×5、イクサバ×2

【立ち回り】
1. アラナンの1アビで火力バフ
2. アテナのダメージカットで防御
3. エッセルの弱体で敵を弱体化
""",
        "tags": ["火属性", "高難易度", "編成例"],
        "source": "gamewith_mock",
        "url": "https://gamewith.jp/granblue/article/show/mock_party1"
    }
]


async def scrape_gamewith_mock(character_limit: Optional[int] = 10) -> List[Dict[str, Any]]:
    """
    モックデータを返す（テスト用）
    
    Args:
        character_limit: 取得キャラ数上限
        
    Returns:
        モックデータ
    """
    logger.info("Using MOCK scraper (for testing)")
    logger.info("To use real GameWith scraper, implement HTML parsing in gamewith_scraper.py")
    
    # 少し遅延を入れて実際のスクレイピングをシミュレート
    await asyncio.sleep(1)
    
    # キャラクターデータ
    characters = MOCK_CHARACTERS.copy()
    if character_limit:
        characters = characters[:character_limit]
    
    # 編成データも追加
    all_data = characters + MOCK_COMPOSITIONS
    
    logger.info(f"Mock scraper returned {len(all_data)} items")
    
    # タイムスタンプを追加
    for item in all_data:
        item["scraped_at"] = datetime.now()
    
    return all_data


if __name__ == "__main__":
    async def main():
        data = await scrape_gamewith_mock(character_limit=10)
        print(f"Scraped {len(data)} items")
        for item in data:
            print(f"  - {item['name']} ({item['type']})")
    
    asyncio.run(main())
