# GameWith実スクレイパー実装状況

## 現状

環境でPlaywrightやBeautifulSoup4が利用できない状況です。

## 2つの選択肢

### オプション1: モックデータで継続（推奨）

**メリット:**
- すぐに開発を進められる
- システム全体の動作確認が可能
- フロントエンド開発に移れる

**実行方法:**
```powershell
# モックデータで実行
python scripts/scrape_and_index.py --limit 10
```

現在のモックデータ:
- ベリアル（闇・評価9.8）
- サンダルフォン（光・評価9.5）
- ノイシュ（土・評価8.5）
- 火属性高難易度編成

### オプション2: 実スクレイパー実装

**必要な作業:**

1. **依存パッケージのインストール**
   ```powershell
   pip install playwright beautifulsoup4 lxml requests
   playwright install chromium
   ```

2. **GameWithのHTML構造を手動調査**
   - ブラウザでhttps://gamewith.jp/granblue/article/show/20722を開く
   - F12でDevToolsを開く
   - Elements タブでキャラカードの構造を確認
   - 以下を特定：
     - キャラカードのCSSセレクタ
     - キャラ名の要素
     - 属性、評価点の要素
     - 詳細ページへのリンク

3. **`gamewith_scraper.py`を実装**

   ```python
   # 実際のHTML構造に基づいて実装
   # 例：
   char_cards = soup.select(".実際のセレクタ")
   for card in char_cards:
       name = card.select_one(".name-selector").get_text(strip=True)
       # ...
   ```

4. **テスト実行**
   ```powershell
   python scripts/scrape_and_index.py --limit 3 --dry-run
   ```

## 推奨フロー

### 今すぐできること: モックデータで開発継続

```powershell
# 1. モックデータでインデックス作成
python scripts/scrape_and_index.py --limit 10

# 2. APIサーバー起動
python run.py

# 3. 新しいキャラで動作確認
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"message\": \"ベリアルについて教えて\"}"

curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"message\": \"サンダルフォンの評価は？\"}"
```

**モックデータでも以下が可能:**
- ✅ RAG検索の動作確認
- ✅ Agent機能のテスト
- ✅ API動作確認
- ✅ フロントエンド開発
- ✅ システム全体の統合テスト

### 後で実スクレイパー実装

Phase 3（Agent拡張）やPhase 4（フロントエンド）を先に進めて、
実スクレイパーは後から追加することもできます。

## 実装例（参考）

もし実装する場合の手動調査方法：

### ブラウザでの確認

```javascript
// GameWithページを開いてコンソールで実行

// キャラカードの数を確認
document.querySelectorAll('tr').length  // テーブル行
document.querySelectorAll('.card').length  // カード形式
document.querySelectorAll('article').length  // 記事形式

// 最初の要素を確認
document.querySelector('tr')
document.querySelector('tr').textContent  // テキスト内容
document.querySelector('tr a').href  // リンク
```

### HTMLの保存

1. GameWithページを開く
2. 右クリック→「ページのソースを表示」
3. 全選択してファイルに保存
4. エディタで開いてキャラカード部分を探す

## 決定してください

**A. モックデータで継続（Phase 3へ）**
- Agent拡張機能の実装
- キャラクター比較ツール
- 編成構築ツール

**B. 実スクレイパー実装（時間かかる）**
- パッケージインストール
- HTML構造調査
- スクレイパー実装
- テスト・デバッグ

どちらで進めますか？
