# API動作確認ガイド

おめでとうございます！🎉 グランブルーRAGシステムのAPIが起動しました。

## 動作確認

### 1. ヘルスチェック

```bash
# Windows PowerShell
curl http://localhost:8000/health

# または
Invoke-WebRequest -Uri http://localhost:8000/health
```

**期待される応答:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-04-14T05:04:55.302Z"
}
```

### 2. チャットAPI テスト

```powershell
# PowerShell
$body = @{
    message = "カタリナについて教えて"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/api/chat `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

**期待される応答:**
```json
{
  "response": "カタリナ（SSR・水属性）について説明します...",
  "sources": [
    {
      "type": "character",
      "name": "カタリナ",
      "url": "https://gbf-wiki.com/index.php?カタリナ",
      "relevance_score": 0.92
    }
  ],
  "suggested_actions": [
    "他のキャラクターを検索",
    "編成例を見る"
  ],
  "conversation_id": "..."
}
```

### 3. 検索API テスト

```powershell
# PowerShell
$body = @{
    query = "水属性 初心者"
    top_k = 3
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/api/search `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

### 4. APIドキュメント確認

ブラウザで以下にアクセス:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## テストクエリ例

### 初心者向け質問
```json
{"message": "水属性で初心者におすすめのキャラは？"}
{"message": "カタリナの使い方を教えて"}
{"message": "初心者向けの水属性編成は？"}
```

### 編成相談
```json
{
  "message": "水属性の高難易度編成を教えて",
  "context": {
    "user_rank": 150,
    "owned_characters": ["カタリナ", "ランスロット"]
  }
}
```

### 武器について
```json
{"message": "レヴィアンゲイズ・マグナの評価は？"}
{"message": "マグナ武器の集め方"}
```

## トラブルシューティング

### ローカルLLMに接続できない

**症状:** チャットAPIが500エラーを返す

**解決策:**
```bash
# Ollamaが起動しているか確認
curl http://localhost:11434/api/tags

# 起動していない場合
ollama serve
```

### Embeddingsが遅い

**症状:** 初回検索が10秒以上かかる

**原因:** HuggingFaceモデルの初回読み込み

**対策:**
- 2回目以降はキャッシュから読み込むため高速化
- または軽量モデルに変更（`.env`）:
  ```
  EMBEDDING_MODEL=intfloat/multilingual-e5-base
  ```

### 検索結果が空

**症状:** `"results": []`

**原因:** データが未登録

**解決策:**
```bash
# データを再セットアップ
set PYTHONPATH=%CD%
python scripts\setup_data.py
```

## 次のステップ

### 1. より多くのデータを追加

現在はサンプルデータのみです。実際のWikiデータを追加:
```bash
# 実装予定
python scripts\scrape_wiki.py
```

### 2. フロントエンド開発

Webチャットインターフェースの構築（Next.js）

### 3. カスタマイズ

- プロンプト調整: `app/agents/agent.py`の`SYSTEM_PROMPT`
- 検索パラメータ: `app/core/config.py`の`retrieval_top_k`など

## API仕様詳細

### POST /api/chat

**リクエスト:**
```json
{
  "message": "質問内容",
  "context": {
    "user_rank": 100,
    "owned_characters": ["キャラ1", "キャラ2"],
    "favorite_element": "水"
  },
  "conversation_id": "optional-conversation-id"
}
```

**レスポンス:**
```json
{
  "response": "AI応答",
  "sources": [...],
  "suggested_actions": [...],
  "conversation_id": "..."
}
```

### POST /api/search

**リクエスト:**
```json
{
  "query": "検索クエリ",
  "filters": {
    "type": "character",
    "element": "水",
    "rarity": "SSR"
  },
  "top_k": 5
}
```

**レスポンス:**
```json
{
  "results": [
    {
      "id": "...",
      "type": "character",
      "name": "カタリナ",
      "content": "...",
      "metadata": {...},
      "score": 0.92
    }
  ],
  "total": 1,
  "query": "検索クエリ"
}
```

## ログ確認

```bash
# エラーログ
cat logs/error.log

# または起動したターミナルで確認
```

問題があればログを確認してください！
