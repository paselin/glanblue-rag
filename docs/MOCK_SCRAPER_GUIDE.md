# GameWithスクレイパー: モックデータ版

## 現状

GameWithの実際のHTML構造を確認する必要があるため、**モックデータ**を使用してシステムをテストできるようにしました。

## モックデータの使用方法

```powershell
# モックデータで10件取得してインデックス
set PYTHONPATH=%CD%
python scripts/scrape_and_index.py --limit 10
```

**モックデータ内容:**
- ベリアル（闇・評価9.8）
- サンダルフォン（光・評価9.5）
- ノイシュ（土・評価8.5）
- 火属性高難易度編成

## 実行結果

```
Starting scrape and index process...
=== Using Mock Scraper (Testing) ===
NOTE: This uses sample data. Implement real scraper in gamewith_scraper.py
Mock data: 4 items

=== Sample Data ===
1. ベリアル (character) - Source: gamewith_mock
2. サンダルフォン (character) - Source: gamewith_mock
3. ノイシュ (character) - Source: gamewith_mock

=== Indexing Documents ===
Indexed 4 chunks from 4 documents
```

## 実際のGameWithスクレイパーを実装するには

### 1. GameWithのHTML構造を確認

ブラウザで https://gamewith.jp/granblue/article/show/20722 を開き、DevToolsでHTML構造を確認。

### 2. セレクタを特定

```javascript
// ブラウザのコンソールで実行
document.querySelectorAll('.character-card').length  // キャラカード数
document.querySelector('.character-card')  // 最初のカードの構造
```

### 3. `gamewith_scraper.py`を実装

```python
# セレクタを実際の構造に合わせて修正
char_cards = soup.select(".actual-selector-here")

for card in char_cards:
    name = card.select_one(".actual-name-selector").get_text(strip=True)
    # ...
```

## 暫定対応: モックデータで開発継続

モックデータでも以下が可能です：
- ✅ インデックス処理のテスト
- ✅ RAG検索の動作確認
- ✅ API/Agent動作確認
- ✅ フロントエンド開発

**実データは後から追加できます！**

## テスト実行

```powershell
# モックデータでインデックス
python scripts/scrape_and_index.py --limit 10

# サーバー起動
python run.py

# テスト（ベリアルについて質問）
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"message\": \"ベリアルについて教えて\"}"
```

## 次のステップ

1. **モックデータでシステム完成**: フロントエンド、機能拡張など
2. **GameWith HTML構造調査**: 実際のページを確認
3. **実スクレイパー実装**: HTML構造に合わせて実装

モックデータでも完全に動作するので、先に進めましょう！
