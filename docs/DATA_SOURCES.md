# データソース戦略

グランブルーファンタジーRAGシステムのデータソース設計と実装詳細

## 📊 データソース概要

| ソース | 種類 | 件数 | 更新頻度 | 優先度 | 実装状況 |
|--------|------|------|----------|--------|----------|
| GameWith | キャラクター評価・攻略 | ~648件 | 毎週 | 🔥 高 | ✅ 完了 |
| Wiki 用語集 | ゲーム用語定義 | ~500件 | 月1回 | 🔷 中 | ✅ 完了 |
| Wiki 俗語集 | コミュニティ用語・俗称 | ~770件 | 月1回 | 🔷 中 | ✅ 完了 |

**合計**: 約1,918件のドキュメント

---

## 🎯 データソースの役割分担

### GameWith（キャラクター特化）

**強み**:
- ✅ 構造化された評価データ（点数・レーティング）
- ✅ 詳細なビルド・編成情報
- ✅ 高難易度クエスト対応情報
- ✅ 初心者向け解説が充実

**取得データ**:
```python
{
    "name": "浴衣アリア",
    "element": "水",
    "rarity": "SSR",
    "rating": 9.9,
    "tags": ["防御", "周回", "回復", "高難易度"],
    "content": "評価点数、使い方、LB振り方、アビリティ..."
}
```

**使用ケース**:
- キャラクター評価を知りたい
- おすすめ編成を教えて
- 初心者向けキャラは？
- 高難易度で使えるキャラは？

---

### Wiki 用語集（ゲーム用語）

**強み**:
- ✅ 公式用語の正確な定義
- ✅ ゲームシステム用語の網羅
- ✅ ストーリー関連の固有名詞

**取得データ例**:
```python
{
    "name": "アウギュステ列島",
    "type": "glossary",
    "glossary_type": "terms",
    "content": "広大な水資源の上を漂う経済特区。観光地として人気が高く..."
}
```

**使用ケース**:
- アウギュステってどこ？
- アーカルムの転世とは？
- 七曜の騎士について教えて

---

### Wiki 俗語集（コミュニティ用語）

**強み**:
- ✅ プレイヤー間の通称・俗語
- ✅ スラング・略語の解説
- ✅ 実戦で使われる言葉

**取得データ例**:
```python
{
    "name": "黒麒麟",
    "type": "glossary", 
    "glossary_type": "slang",
    "content": "マルチバトル「黒麒麟」の略称。救援によく流れる..."
}
```

**使用ケース**:
- 「水ゾ」って何？
- 「シエテ砲」とは？
- マグナ編成って？
- ハイランダーって？

---

## 🛠️ 実装詳細

### GameWithスクレイパー

**技術スタック**: `requests` + `BeautifulSoup` + `lxml`

**処理フロー**:
1. キャラクター一覧ページから全キャラURLを取得
2. 各キャラクター詳細ページから情報を抽出
3. 評価点・属性・タグなどのメタデータを構造化

**主要セレクター**:
```python
# 一覧ページ
character_links = soup.select('td > a[href*="/article/show/"]')

# 詳細ページ
rating = soup.select_one('.評価点数セレクター')
element = soup.select_one('.属性セレクター')
tags = soup.select('.タグセレクター')
```

**特徴**:
- ✅ MacOS/Windows両対応
- ✅ Playwright不要（シンプル）
- ✅ レート制限対応（2秒/リクエスト）

---

### Wikiスクレイパー

**技術スタック**: `requests` + `BeautifulSoup` + `lxml` (XPath)

**処理フロー**:
1. 五十音順ページ（あ行、か行...）を順次取得
2. XPath `//table/tr/td[2]` でメインコンテンツ取得
3. `h3/h4` + 次の要素パターンで用語抽出

**主要コード**:
```python
# XPathでメインコンテンツ取得
import lxml.html
tree = lxml.html.fromstring(response.content)
content_elements = tree.xpath('//table/tr/td[2]')

# h3/h4 + 定義のパターン抽出
for heading in soup.find_all(['h3', 'h4']):
    term = heading.get_text(strip=True).replace('†', '')
    definition = heading.find_next_sibling(['p', 'div', 'ul'])
```

**対象ページ**:
```python
# 用語集
"用語集/あ行", "用語集/か行", ..., "用語集/アルファベット、数字他"

# 俗語集  
"俗語集/あ行", "俗語集/か行", ..., "俗語集/アルファベット、数字他"
```

---

## 📈 データ品質管理

### メタデータフィルタリング

ChromaDBの制限に対応:
```python
# リスト型メタデータを文字列化
if isinstance(value, list):
    filtered_metadata[key] = ", ".join(str(v) for v in value)

# dict型は除外
if isinstance(value, dict):
    continue
```

### データ検証

```python
# 必須フィールドチェック
assert doc.page_content, "Content is empty"
assert doc.metadata.get("source"), "Source missing"

# 文字数制限
assert len(doc.page_content) < 10000, "Content too long"
```

---

## 🚀 使用方法

### 基本コマンド

```bash
# テスト実行（キャラ10件 + Wiki全件）
python scripts/scrape_and_index.py --limit 10 --wiki

# GameWith全件取得（約32分）
python scripts/scrape_and_index.py --all

# Wiki用語のみ取得（約5分）
python scripts/scrape_and_index.py --limit 0 --wiki

# 高速モード（詳細取得スキップ）
python scripts/scrape_and_index.py --limit 100 --no-details
```

### Windowsバッチファイル

```powershell
# 仮想環境を自動有効化
scripts\scrape.bat --all --wiki
```

### ドライランモード

```bash
# データ取得のみ（インデックス化なし）
python scripts/scrape_and_index.py --limit 5 --dry-run
```

---

## 📊 パフォーマンス

### 実行時間

| 設定 | GameWith | Wiki | 合計 |
|------|----------|------|------|
| テスト（10件） | 30秒 | 25秒 | 55秒 |
| 中規模（100件） | 5分 | 25秒 | 5.5分 |
| **全件** | **32分** | **5分** | **37分** |

### データ量

```
GameWith:   648件 × 平均1,500文字 = 約970KB
Wiki用語:   500件 × 平均  300文字 = 約150KB
Wiki俗語:   770件 × 平均  400文字 = 約300KB
---------------------------------------------
合計:     1,918件                = 約1.4MB
```

### ベクトルDB容量

```
ドキュメント数: 1,918件
チャンク数:     約3,000-4,000チャンク (500文字/チャンク)
埋め込み次元:   384次元 (intfloat/multilingual-e5-small)
DB容量:         約50-80MB (ChromaDB)
```

---

## 🔄 更新戦略

### 自動更新（Phase 3で実装予定）

```python
# 週次更新スケジュール
schedule.every().monday.at("03:00").do(update_gamewith)
schedule.every().monday.at("04:00").do(update_wiki)
schedule.every().monday.at("05:00").do(rebuild_index)
```

### 差分更新

```python
# 既存データと比較
new_characters = set(scraped_ids) - set(existing_ids)
updated_characters = [id for id in existing_ids 
                      if hash_changed(id)]

# 差分のみ更新
indexer.add_documents(new_characters)
indexer.update_documents(updated_characters)
```

---

## 🧪 テスト

### スクレイパー単体テスト

```bash
# GameWithスクレイパー
python app/services/scraper/gamewith_simple_scraper.py

# Wikiスクレイパー
python app/services/scraper/wiki_scraper.py
```

### 統合テスト

```bash
# エンドツーエンド
python scripts/scrape_and_index.py --limit 3 --wiki --dry-run
```

---

## 🔮 将来の拡張

### Phase 2.5（オプション）

- [ ] **Wikiキャラクターページ**: 全キャラ一覧からキャラ詳細抽出
- [ ] **ゲームシステム用語集**: 別ページの用語も取得
- [ ] **攻略まとめ**: クエスト攻略情報

### Phase 3以降

- [ ] **公式お知らせ**: 最新イベント情報
- [ ] **バランス調整情報**: キャラ強化/弱体化履歴
- [ ] **画像データ**: キャラ画像、アイコン
- [ ] **動画データ**: YouTube攻略動画の文字起こし

---

## 🐛 既知の問題と対策

### 問題1: Playwrightの不安定性（MacOS）

**問題**: `TargetClosedError: Browser has been closed`

**対策**: 
- ✅ `requests` + `BeautifulSoup`に変更済み
- ✅ MacOS/Windows両対応

### 問題2: メタデータ型エラー

**問題**: ChromaDBがlist型を受け付けない

**対策**:
```python
# カスタムフィルター実装
def _filter_metadata(metadata: dict) -> dict:
    filtered = {}
    for key, value in metadata.items():
        if isinstance(value, list):
            filtered[key] = ", ".join(str(v) for v in value)
        elif isinstance(value, (str, int, float, bool)):
            filtered[key] = value
    return filtered
```

### 問題3: レート制限

**問題**: 短時間に大量リクエストでブロック

**対策**:
```python
# 設定可能な遅延
time.sleep(settings.scraper_delay)  # デフォルト2秒
```

---

## 📚 参考資料

### データソースURL

- **GameWith**: https://xn--bck3aza1a2if6kra4ee0hf.gamewith.jp/
- **グラブルWiki**: https://gbf-wiki.com/
  - 用語集: `index.php?用語集`
  - 俗語集: `index.php?俗語集`
  - キャラ一覧: `index.php?全キャラクター一覧`

### 関連ドキュメント

- [DESIGN.md](../DESIGN.md) - システム全体設計
- [README.md](../README.md) - プロジェクト概要
- [app/services/scraper/](../app/services/scraper/) - スクレイパー実装

---

## 🤝 貢献

データソースの追加・改善提案は大歓迎です！

1. 新しいデータソースの提案（Issue作成）
2. スクレイパーの改善（Pull Request）
3. データ品質の報告（Issue作成）

---

**最終更新**: 2026-04-15  
**バージョン**: MVP (Phase 2完了)
