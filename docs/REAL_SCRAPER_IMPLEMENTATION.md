# 実スクレイパー実装ガイド

## ステップ1: HTML構造の分析

### 分析ツールの実行

```powershell
# Windowsで
set PYTHONPATH=%CD%
python scripts/analyze_gamewith.py
```

このスクリプトは：
1. GameWithのページをブラウザで開く
2. HTML構造を分析してログに出力
3. HTMLファイルを保存（`gamewith_*.html`）
4. ブラウザを開いたまま手動確認可能

### 確認するポイント

#### キャラクター一覧ページ
- [ ] キャラカードのCSSセレクタ
- [ ] キャラ名の要素
- [ ] 属性の要素
- [ ] 評価点の要素
- [ ] 詳細ページへのリンク

#### キャラクター詳細ページ
- [ ] 記事本文のセレクタ
- [ ] 見出しの構造
- [ ] テーブルの形式
- [ ] アビリティ情報の配置

## ステップ2: セレクタの特定

### ブラウザのDevToolsで確認

```javascript
// ブラウザのコンソールで実行

// キャラクター一覧
document.querySelectorAll('[実際のセレクタ]').length

// 最初の要素を見る
document.querySelector('[実際のセレクタ]')

// キャラ名を取得
document.querySelector('[実際のセレクタ] .name').textContent
```

### よくあるセレクタパターン

```css
/* キャラカード */
.character-card
.chara-list-item
article.character
.ranking-item

/* キャラ名 */
.character-name
.chara-name
h3.name
.title

/* 属性 */
.element
.attr
[data-element]
img[alt*="属性"]

/* 評価点 */
.rating
.score
.point
```

## ステップ3: スクレイパーの実装

分析結果を基に `gamewith_scraper.py` を更新：

```python
async def scrape_character_list(self) -> List[Dict[str, Any]]:
    content = await self._fetch_page(url)
    soup = BeautifulSoup(content, "lxml")
    
    # 実際のセレクタに置き換え
    char_cards = soup.select("[実際のセレクタ]")
    
    for card in char_cards:
        # 名前
        name_elem = card.select_one("[名前のセレクタ]")
        name = name_elem.get_text(strip=True) if name_elem else None
        
        # 属性
        element_elem = card.select_one("[属性のセレクタ]")
        # ...
```

## ステップ4: テスト実行

```powershell
# 実装したスクレイパーをテスト
python app/services/scraper/gamewith_scraper.py
```

## ステップ5: データ収集

```powershell
# 少量でテスト
python scripts/scrape_and_index.py --limit 3 --dry-run

# 問題なければ本番
python scripts/scrape_and_index.py --limit 10
```

## トラブルシューティング

### ページが読み込まれない

```python
# タイムアウトを延長
await page.goto(url, timeout=60000)
await page.wait_for_load_state("networkidle")
await asyncio.sleep(3)  # 追加の待機
```

### 要素が見つからない

```python
# 複数のセレクタを試す
selectors = [
    ".selector1",
    ".selector2",
    "div[class*='partial-match']"
]

for selector in selectors:
    elements = soup.select(selector)
    if elements:
        break
```

### 動的コンテンツ

```python
# JavaScriptで生成される内容の場合
await page.wait_for_selector(".target-element", timeout=10000)
```

## 実装チェックリスト

### 基本機能
- [ ] `scrape_character_list()` - 一覧取得
- [ ] `scrape_character_detail()` - 詳細取得
- [ ] エラーハンドリング
- [ ] レート制限（delay）

### データ抽出
- [ ] キャラ名
- [ ] 属性（火/水/土/風/光/闇）
- [ ] レアリティ（SSR/SR/R）
- [ ] 評価点
- [ ] 詳細URL
- [ ] 本文コンテンツ

### 品質チェック
- [ ] 空データのスキップ
- [ ] 重複の除外
- [ ] ログ出力
- [ ] タイムスタンプ付与

## 完成したらテスト

```powershell
# 1. 構造分析
python scripts/analyze_gamewith.py

# 2. スクレイパー単体テスト  
python app/services/scraper/gamewith_scraper.py

# 3. インデックステスト
python scripts/scrape_and_index.py --limit 3 --dry-run

# 4. 本番実行
python scripts/scrape_and_index.py --limit 10

# 5. API確認
python run.py
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"message\": \"最新キャラの評価は？\"}"
```

## 次のステップ

実装完了後：
1. データ品質の確認
2. 定期更新スクリプトの作成
3. エラー通知の実装
4. スクレイピング結果の可視化

頑張ってください！
