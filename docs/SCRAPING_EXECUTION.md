# GameWith スクレイピング実行ガイド

## 実行方法

### Windows（推奨）

```powershell
# 1. 仮想環境を有効化
venv\Scripts\activate

# 2. PYTHONPATHを設定
set PYTHONPATH=%CD%

# 3. スクレイパーを実行

# テスト（10件・dry-run）
python scripts\scrape_and_index.py --limit 10 --dry-run

# 本番（10件をインデックス）
python scripts\scrape_and_index.py --limit 10

# 全データ（648件）
python scripts\scrape_and_index.py --limit 648
```

または**便利スクリプト**を使用：

```powershell
# テスト
scripts\scrape.bat --limit 10 --dry-run

# 本番
scripts\scrape.bat --limit 10
```

### Mac/Linux

```bash
# 便利スクリプトを使用（推奨）
./scripts/scrape.sh --limit 10 --dry-run
./scripts/scrape.sh --limit 10

# または手動で
source venv/bin/activate
export PYTHONPATH=$(pwd)
python scripts/scrape_and_index.py --limit 10
```

## 期待される出力

### データプレビュー例

```
=== SCRAPED DATA PREVIEW ===

[1] 浴衣アリア
    Type: character
    Element: 水
    Rarity: SSR
    Rating: 9.9
    Tags: 新キャラ, 水着
    Source: gamewith
    URL: https://xn--bck3aza1a2if6kra4ee0hf.gamewith.jp/article/show/547954
    Content Preview:
      浴衣アリア（SSR・水属性） 【評価点】 9.9/10点 【特徴】 50% - 自分 - 奥義枠...

[2] 水着アンスリア
    Type: character
    Element: 光
    Rating: 9.6
    ...

=== STATISTICS ===

属性別キャラクター数:
  闇: 120件
  光: 115件
  火: 110件
  水: 108件
  風: 105件
  土: 90件

評価点:
  平均: 8.45
  最高: 10.0
  最低: 6.0
  評価あり: 648件 / 648件

よくあるタグ（上位10件）:
  リミテッド: 85件
  新キャラ: 42件
  十天衆: 10件
  水着/浴衣: 35件
  ...
```

## データの確認

### 1. プレビューで確認

```powershell
# dry-runで実行（インデックスせずに確認のみ）
scripts\scrape.bat --limit 50 --dry-run
```

### 2. インデックス実行

問題なければ：

```powershell
# 段階的に増やす
scripts\scrape.bat --limit 10     # 10件
scripts\scrape.bat --limit 50     # 50件
scripts\scrape.bat --limit 648    # 全件
```

### 3. APIで動作確認

```powershell
# サーバー起動
python run.py

# 新しいキャラで検索
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"message\": \"ベリアルの評価は？\"}"

curl -X POST http://localhost:8000/api/search -H "Content-Type: application/json" -d "{\"query\": \"リミテッド 闇属性\", \"top_k\": 5}"
```

## トラブルシューティング

### HTMLファイルが見つからない

```powershell
# ファイルを確認
dir gamewith_character_list.html

# プロジェクトルートにあることを確認
# なければダウンロードまたは配置
```

### 文字化け

```powershell
# Windowsでエンコーディング設定
chcp 65001
set PYTHONIOENCODING=utf-8
```

### メモリ不足（648件全部の場合）

```powershell
# 分割して実行
# 既存データは上書きされないので追加される
scripts\scrape.bat --limit 100
scripts\scrape.bat --limit 200
# ...
```

## データの品質確認

インデックス後、以下で確認：

```powershell
# ベクトルストアの統計
python -c "from app.rag.vector_store import get_vector_store; vs = get_vector_store(); print(vs.get_collection_stats())"

# サンプル検索
curl -X POST http://localhost:8000/api/search -H "Content-Type: application/json" -d "{\"query\": \"評価の高いキャラ\", \"top_k\": 10}"
```

準備完了です！実行してみてください 🚀
