# クイックスタートガイド

## 前提条件

- Python 3.10以上
- 8GB以上のメモリ推奨
- ローカルLLM (Ollama推奨) または OpenAI互換API

## 5分でスタート

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd granblue-rag
```

### 2. 仮想環境の作成

```bash
python -m venv venv

# アクティベート
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. ローカルLLMのセットアップ

#### Ollama（推奨）

```bash
# Ollamaのインストール
curl -fsSL https://ollama.com/install.sh | sh

# モデルのダウンロード
ollama pull qwen2.5:14b

# サーバー起動
ollama serve
```

### 5. 環境変数の設定

```bash
cp .env.example .env
```

`.env`の内容（デフォルトのまま使用可能）：

```bash
# ローカルLLM設定
OPENAI_API_KEY=dummy-key
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_MODEL=qwen2.5:14b

# HuggingFace Embeddings（完全無料）
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=intfloat/multilingual-e5-large
EMBEDDING_DEVICE=cpu
```

### 6. サンプルデータのセットアップ

```bash
# Windowsの場合
set PYTHONPATH=%CD%
python scripts/setup_data.py

# Linux/Macの場合
export PYTHONPATH=$(pwd)
python scripts/setup_data.py
```

初回実行時はEmbeddingsモデルのダウンロードに5-10分かかります。

### 7. サーバー起動

```bash
python app/main.py
```

サーバーが http://localhost:8000 で起動します。

### 8. 動作確認

別のターミナルで：

```bash
# ヘルスチェック
curl http://localhost:8000/health

# チャットテスト
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "カタリナについて教えて"}'

# 検索テスト
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "水属性", "top_k": 3}'
```

## 成功！

これでグラブルRAGシステムが稼働しました 🎉

## 次のステップ

1. **Wikiスクレイピング**: 実際の攻略データを収集
   ```bash
   # 実装予定
   python scripts/scrape_wiki.py
   ```

2. **フロントエンド構築**: Webチャットインターフェース
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **カスタマイズ**: プロンプトやモデルの調整

## トラブルシューティング

### Embeddings モデルのダウンロードが遅い

軽量モデルに変更：
```bash
EMBEDDING_MODEL=intfloat/multilingual-e5-base
```

### ローカルLLMに接続できない

```bash
# Ollamaが起動しているか確認
curl http://localhost:11434/api/tags

# モデルがダウンロードされているか確認
ollama list
```

### メモリ不足

```bash
# より軽量なモデルを使用
ollama pull qwen2.5:7b
OPENAI_MODEL=qwen2.5:7b
```

詳細は [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) を参照。

## 詳細ドキュメント

- [ローカルLLMセットアップ](./LOCAL_LLM_SETUP.md)
- [HuggingFace Embeddings](./HUGGINGFACE_SETUP.md)
- [設計書](../DESIGN.md)
- [README](../README.md)
