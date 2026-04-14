"""
Script to populate initial data from scraped sources.
"""
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.scraper.wiki_scraper import scrape_wiki
from app.services.indexer import get_indexer
from app.core.logging import setup_logging

logger = setup_logging()


# Sample data for testing (before implementing full scraper)
SAMPLE_DATA: List[Dict[str, Any]] = [
    {
        "id": "char_katalina",
        "type": "character",
        "name": "カタリナ",
        "element": "水",
        "rarity": "SSR",
        "content": """
カタリナ（SSR・水属性）

【基本情報】
タイプ: 防御
武器種: 剣
CV: 沢城みゆき

【アビリティ】
1. エンチャントランズ
   - 味方全体のHP回復（上限1000）
   - 再生効果付与（3ターン）

2. ライトウォール
   - 味方全体にダメージカット（30%/2ターン）
   - 防御UP効果

3. フロストネイル
   - 敵に水属性ダメージ
   - 防御DOWN付与

【評価】
初心者向けの優秀なサポートキャラクター。
回復とダメージカットで安定した戦闘が可能。
序盤から終盤まで幅広く活躍できる。

【おすすめ編成】
- 初心者向け水属性パーティのサブアタッカー兼ヒーラー
- マグナ編成での安定要員
- 高難易度クエストでの生存率向上

【入手方法】
サプライズチケット交換可能
""",
        "tags": ["初心者向け", "サポート", "回復", "ダメージカット"],
        "source_url": "https://gbf-wiki.com/index.php?カタリナ",
    },
    {
        "id": "char_lancelot",
        "type": "character",
        "name": "ランスロット",
        "element": "水",
        "rarity": "SSR",
        "content": """
ランスロット（SSR・水属性）

【基本情報】
タイプ: 攻撃
武器種: 剣
CV: 小野友樹

【アビリティ】
1. サザンクロス
   - 敵に3回水属性ダメージ
   - 自分に攻撃UP効果

2. ミゼラブルミスト相当の弱体効果
   - 敵の攻撃DOWN
   - 敵の防御DOWN

3. 双剣乱舞
   - 敵に5回水属性ダメージ
   - 自分に連続攻撃確率UP

【評価】
水属性の優秀なアタッカー。
高い火力と弱体効果を持ち、序盤から活躍。
特に連続攻撃を活かした短期戦で強力。

【おすすめ編成】
- 水属性マグナ編成のメインアタッカー
- 古戦場などの周回クエスト
- 短期決戦型の編成

【入手方法】
ガチャ排出
サプライズチケット交換可能
""",
        "tags": ["アタッカー", "連続攻撃", "弱体", "周回"],
        "source_url": "https://gbf-wiki.com/index.php?ランスロット",
    },
    {
        "id": "party_water_beginner",
        "type": "party_composition",
        "name": "水属性初心者向け編成",
        "element": "水",
        "content": """
水属性初心者向けパーティ編成

【推奨編成】
メイン: グラン/ジータ（主人公）
- ジョブ: ダークフェンサー
- アビリティ: ミゼラブルミスト、アローレイン

サブ1: カタリナ（SSR）
- 役割: 回復・サポート
- ダメージカットと回復で安定性UP

サブ2: ランスロット（SSR）
- 役割: メインアタッカー
- 高火力で素早く敵を倒す

サブ3: ヨダルラーハ（SSR）
- 役割: 奥義アタッカー
- 初心者の周回を効率化

【武器編成】
- メイン武器: SRマグナ武器（レヴィアンゲイズ等）
- サブ武器: SRマグナ武器を並べる
- 徐々にSSRマグナ武器に入れ替え

【召喚石】
- メイン: カーバンクル（水）
- サブ: 攻撃力が高い召喚石

【立ち回り】
1. 主人公のミゼラブルミストで弱体
2. ランスロットで攻撃
3. ヨダルラーハの奥義で一気にダメージ
4. カタリナで回復・カット

【次のステップ】
- マグナ武器（リヴァイアサン）の収集
- 十天衆ウーノの取得を目指す
- リミテッド武器の入手
""",
        "tags": ["初心者向け", "編成例", "水属性", "マグナ"],
        "tier": "初心者",
    },
    {
        "id": "weapon_levi_dagger",
        "type": "weapon",
        "name": "レヴィアンゲイズ・マグナ",
        "element": "水",
        "rarity": "SSR",
        "content": """
レヴィアンゲイズ・マグナ（SSR・短剣）

【基本情報】
武器種: 短剣
属性: 水
入手方法: リヴァイアサン・マグナ討伐戦

【武器スキル】
海神方陣・攻刃II
- 水属性キャラの攻撃力UP（方陣）
- スキルLv15で18%UP

【奥義効果】
マグナ・ウェーブ
- 水属性ダメージ（特大）
- 味方全体のHP回復

【評価】
水属性マグナ編成の基本武器。
攻刃IIなので通常の攻刃武器より倍率が高い。
初心者は最優先で4～5本集めるべき。

【運用方法】
- 武器編成に4～5本編成
- 最終上限解放（4凸）を目指す
- スキルレベルは15まで上げる

【ドロップ場所】
リヴァイアサン・マグナ
確定流し、ワンパン流しで集める
""",
        "tags": ["マグナ武器", "攻刃", "水属性", "初心者向け"],
        "weapon_type": "短剣",
    },
]


async def setup_initial_data():
    """Setup initial data in vector store."""
    logger.info("Setting up initial data...")
    
    # Use sample data for now
    # In production, you'd scrape from actual sources
    documents = SAMPLE_DATA
    
    # Uncomment to use scraper when implemented
    # documents = await scrape_wiki()
    
    # Index documents
    indexer = get_indexer()
    num_chunks = indexer.process_and_index(documents)
    
    logger.info(f"Setup complete! Indexed {num_chunks} chunks from {len(documents)} documents")
    
    return num_chunks


if __name__ == "__main__":
    asyncio.run(setup_initial_data())
