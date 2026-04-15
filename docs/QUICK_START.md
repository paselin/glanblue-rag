# クイックスタートガイド

グランブルーファンタジーRAGシステムを5分で起動

## 🚀 最速セットアップ

### 1. 環境構築（2分）

```bash
# リポジトリクローン
git clone <repository-url>
cd granblue-rag

# 仮想環境作成・有効化
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt
```

### 2. データ収集（2分）

```bash
# テストデータ取得（キャラ10件 + Wiki全件）
python scripts/scrape_and_index.py --limit 10 --wiki

# または Windows
scripts\scrape.bat --limit 10 --wiki
```

出力例:
```
2026-04-15 14:00:00 | INFO | Scraping GameWith...
2026-04-15 14:00:30 | INFO | GameWith: 10 items
2026-04-15 14:00:30 | INFO | Scraping Wiki...  
2026-04-15 14:01:00 | INFO | Wiki: 1270 items
2026-04-15 14:01:00 | INFO | Indexing 1280 documents...
2026-04-15 14:01:30 | INFO | Successfully indexed 1280 documents
```

### 3. API起動（1分）

```bash
# サーバー起動
python app/main.py

# または Windows
run.bat
```

起動確認:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 💬 使ってみる

### ブラウザでテスト

1. **APIドキュメント**: http://localhost:8000/docs
2. **ヘルスチェック**: http://localhost:8000/health

### curlでテスト

```bash
# チャット
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "水着キャラでおすすめは？",
    "conversation_id": "test-001"
  }'
```

レスポンス例:
```json
{
  "response": "水着キャラでおすすめは...",
  "sources": [
    {
      "title": "浴衣アリア",
      "source": "gamewith",
      "url": "https://..."
    }
  ]
}
```

### 検索テスト

```bash
# セマンティック検索
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "高難易度で使えるキャラ",
    "limit": 5
  }'
```

---

## 🎯 よくある質問

### Q: データが取れない

**A**: 環境変数を確認
```bash
# .envファイル作成（任意）
SCRAPER_DELAY=2
SCRAPER_USER_AGENT="Mozilla/5.0..."
```

### Q: メモリ不足エラー

**A**: チャンクサイズを調整
```python
# app/services/indexer.py
chunk_size = 300  # デフォルト500から減らす
```

### Q: APIが遅い

**A**: ローカルLLMの設定確認
```python
# app/core/config.py
OLLAMA_URL = "http://localhost:11434"  # Ollama起動確認
OLLAMA_MODEL = "llama3.1:8b"  # 軽量モデル推奨
```

---

## 📖 次のステップ

1. **全データ取得**: `scripts\scrape.bat --all --wiki` (37分)
2. **カスタマイズ**: [設定ガイド](CONFIGURATION.md)
3. **フロントエンド**: Phase 3で実装予定

---

## 🆘 トラブルシューティング

### Windows: `scrape.bat`が動かない

```powershell
# PowerShellで実行
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\scrape.bat --limit 10
```

### Mac: `permission denied`

```bash
# 実行権限付与
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

### pip install失敗

```bash
# pipアップグレード
python -m pip install --upgrade pip

# 個別インストール
pip install langchain langchain-community chromadb
```

---

**所要時間**: 初回セットアップ 5分、全データ取得 37分  
**推奨環境**: Python 3.10+, RAM 8GB+, Disk 5GB+

[詳細ドキュメント](../README.md) | [設計書](../DESIGN.md) | [データソース](DATA_SOURCES.md)
