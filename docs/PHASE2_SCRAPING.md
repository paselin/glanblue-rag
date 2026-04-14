# Phase 2: データスクレイピング実装

## 概要

GameWithを優先データソースとして、グランブルーファンタジーの攻略情報を自動収集します。

## 実装内容

### 1. GameWithスクレイパー

**優先度が高い理由:**
- 最新の評価・ランキング情報
- 初心者向けガイドが充実
- 編成例が豊富
- 更新頻度が高い

**実装ファイル:** `app/services/scraper/gamewith_scraper.py`

**収集するデータ:**
- SSRキャラクター一覧（評価点付き）
- キャラクター詳細ページ
- 編成ガイド
- 初心者ガイド
- 武器情報

### 2. データ収集スクリプト

**ファイル:** `scripts/scrape_and_index.py`

**使い方:**

```bash
# テスト実行（3件のみ、インデックスしない）
python scripts/scrape_and_index.py --limit 3 --dry-run

# GameWithから10件取得してインデックス
python scripts/scrape_and_index.py --limit 10

# 全データ取得（時間がかかります）
python scripts/scrape_and_index.py --all

# WikiとGameWith両方から取得
python scripts/scrape_and_index.py --gamewith --wiki --limit 20
```

### 3. コマンドラインオプション

```
--gamewith       GameWithから取得（デフォルト: True）
--wiki           Wikiからも取得（デフォルト: False）
--limit N        キャラクター数上限（デフォルト: 10）
--dry-run        スクレイピングのみでインデックスしない
--all            全キャラクター取得（制限なし）
```

## データ構造

### スクレイピング結果

```python
{
    "name": "カタリナ",
    "element": "水",
    "rarity": "SSR",
    "type": "character",
    "url": "https://gamewith.jp/granblue/article/show/12345",
    "rating": 9.5,  # GameWith評価点
    "content": "詳細な攻略情報...",
    "tags": ["初心者向け", "サポート"],
    "source": "gamewith",
    "scraped_at": "2026-04-14T05:30:00"
}
```

## 実行手順

### 1. Playwrightブラウザの確認

```bash
playwright install chromium
```

### 2. テスト実行

```bash
# Windowsで
set PYTHONPATH=%CD%
python scripts/scrape_and_index.py --limit 3 --dry-run
```

**期待される出力:**
```
Starting scrape and index process...
=== Scraping GameWith (Priority Source) ===
Scraping SSR character list from GameWith
Found 100 character elements
Scraping character 1/3: カタリナ
Scraping character 2/3: ランスロット
Scraping character 3/3: ヨダルラーハ
GameWith: Scraped 3 items

=== Sample Data ===
1. カタリナ (character) - Source: gamewith
   Preview: カタリナ（SSR・水属性）水属性の優秀なサポートキャラ...
2. ランスロット (character) - Source: gamewith
3. ヨダルラーハ (character) - Source: gamewith

Dry run mode - skipping indexing
```

### 3. 本番実行（10件インデックス）

```bash
python scripts/scrape_and_index.py --limit 10
```

### 4. 動作確認

```bash
# サーバー起動
python run.py

# チャット確認
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"message\": \"最新のキャラ評価を教えて\"}"
```

## 注意事項

### レート制限

- デフォルト: 各ページ取得後2秒待機（`.env`の`SCRAPER_DELAY`）
- サーバーに負荷をかけないよう配慮

### エラーハンドリング

- 個別ページのエラーはスキップして継続
- 全体のエラーはログに記録

### データの重複

- ドキュメントIDは `{source}_{type}_{name}` で生成
- 同じキャラの再スクレイピングは上書き

## トラブルシューティング

### "Browser not found"

```bash
playwright install chromium
```

### "Timeout waiting for page"

`.env`でタイムアウトを延長:
```
SCRAPER_TIMEOUT=60000  # 60秒
```

### スクレイピングが遅い

並列数を増やす（将来の拡張）または`SCRAPER_DELAY`を減らす:
```
SCRAPER_DELAY=1  # 1秒に短縮（注意: サーバー負荷）
```

### HTML構造の変更

GameWithのHTML構造が変わった場合:
1. ブラウザでページを開く
2. DevToolsで要素を確認
3. `gamewith_scraper.py`のセレクタを更新

## 次のステップ

1. **テスト実行**: `--dry-run`で動作確認
2. **少量取得**: `--limit 10`で実データ取得
3. **段階的拡大**: 問題なければ`--limit 50`、`--all`へ
4. **定期実行**: cronやタスクスケジューラで自動化

## カスタマイズ

### 他のページも取得したい場合

`gamewith_scraper.py`の`PRIORITY_PAGES`に追加:

```python
PRIORITY_PAGES = {
    "character_list": "/article/show/20722",
    "weapon_ranking": "/article/show/xxxxx",  # 追加
    "summon_guide": "/article/show/yyyyy",    # 追加
}
```

### 取得項目を増やす

`scrape_character_detail()`メソッドで追加の情報を抽出:

```python
# 例: おすすめ度を取得
recommend_elem = soup.select_one(".recommend-level")
if recommend_elem:
    detail["recommend_level"] = recommend_elem.get_text(strip=True)
```

これでPhase 2の準備が完了です！
