# Granblue Fantasy RAG System

グランブルーファンタジーの攻略情報を提供するAI Agent RAGシステム

## 概要

ローカルLLMまたはOpenAI互換APIを使用したLLMエージェントとベクトルデータベースを組み合わせ、グラブルの攻略情報（キャラクター、武器、編成、クエスト等）を検索・分析し、ユーザーの質問に答えるシステムです。

## 主な機能

- 💬 チャット形式での攻略相談
- 🔍 キャラクター・武器・編成情報の検索
- 🤖 LLMエージェントによる最適なアドバイス
- 📊 情報源の明示と信頼性の確保
- 🖥️ ローカルLLM対応（Ollama、LM Studio等）

## 技術スタック

- **Backend**: Python 3.11+, FastAPI
- **LLM**: ローカルLLM (Ollama/LM Studio) or OpenAI API
- **Agent Framework**: LangChain
- **Vector DB**: ChromaDB
- **Embeddings**: HuggingFace (multilingual-e5) or OpenAI
- **Scraping**: Playwright, BeautifulSoup4

## セットアップ

### 1. 依存関係のインストール

```bash
# Python仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# パッケージのインストール
pip install -r requirements.txt

# Playwrightブラウザのインストール
playwright install chromium
```

### 2. ローカルLLMのセットアップ

**推奨: Ollama**
```bash
# Ollamaのインストール
curl -fsSL https://ollama.com/install.sh | sh

# 日本語モデルのダウンロード
ollama pull qwen2.5:14b

# サーバー起動
ollama serve
```

詳細は [docs/LOCAL_LLM_SETUP.md](./docs/LOCAL_LLM_SETUP.md) を参照

### 3. 環境変数の設定

```bash
# .envファイルを作成
cp .env.example .env

# .envファイルを編集
# ローカルLLM使用の場合:
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_MODEL=qwen2.5:14b
EMBEDDING_PROVIDER=huggingface
```

### 4. 初期データのセットアップ

```bash
# サンプルデータをベクトルDBに投入
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python scripts/setup_data.py

# または
./scripts/run_setup.sh
```

### 5. サーバーの起動

```bash
# 開発サーバーを起動
python app/main.py

# または
uvicorn app.main:app --reload
```

サーバーは http://localhost:8000 で起動します。

## API使用例

### チャットAPI

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "水属性の初心者向けキャラを教えて",
    "context": {
      "user_rank": 50
    }
  }'
```

### 検索API

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "水属性 SSR",
    "filters": {
      "element": "水",
      "rarity": "SSR"
    },
    "top_k": 5
  }'
```

## ディレクトリ構成

```
granblue-rag/
├── app/
│   ├── api/endpoints/      # APIエンドポイント
│   ├── agents/             # LLMエージェント
│   │   └── tools/          # エージェントツール
│   ├── core/               # コア設定
│   ├── models/             # データモデル
│   ├── rag/                # RAG処理
│   └── services/           # サービスレイヤー
│       └── scraper/        # Webスクレイピング
├── data/                   # データディレクトリ
│   ├── raw/                # 生データ
│   ├── processed/          # 処理済みデータ
│   └── vector_db/          # ベクトルDB
├── docs/                   # ドキュメント
├── scripts/                # ユーティリティスクリプト
└── tests/                  # テスト
```

## 開発

### テストの実行

```bash
pytest tests/
```

### コードフォーマット

```bash
# フォーマット
black app/ scripts/

# リント
ruff check app/ scripts/
```

## ロードマップ

### Phase 1: MVP ✅
- [x] 基本的なRAG機能
- [x] キャラクター情報のサンプルデータ
- [x] チャット・検索API
- [x] ローカルLLM対応

### Phase 2: スクレイピング（次のステップ）
- [ ] Wiki完全スクレイピング実装
- [ ] GameWithデータ取得
- [ ] 自動データ更新

### Phase 3: Agent拡張
- [ ] 編成構築ツール
- [ ] キャラクター比較ツール
- [ ] クエスト攻略アドバイス

### Phase 4: フロントエンド
- [ ] Webチャットインターフェース（Next.js）
- [ ] リッチコンテンツ表示
- [ ] ユーザー設定管理

## トラブルシューティング

### ChromaDBの初期化エラー

```bash
# データディレクトリを削除して再作成
rm -rf data/vector_db/*
python scripts/setup_data.py
```

### Embeddingsモデルのダウンロードが遅い

初回起動時にHuggingFaceからモデルをダウンロードします（数GB）。
軽量モデルに変更する場合:
```bash
EMBEDDING_MODEL=intfloat/multilingual-e5-base
```

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します！

## 詳細設計

詳細な設計書は [DESIGN.md](./DESIGN.md) を参照してください。
ローカルLLMのセットアップは [docs/LOCAL_LLM_SETUP.md](./docs/LOCAL_LLM_SETUP.md) を参照してください。
