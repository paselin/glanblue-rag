# ローカルLLMセットアップガイド

## 概要

このプロジェクトはローカルLLM（Ollama、LM Studio、vLLM等）に対応しています。

## 推奨セットアップ

### オプション1: Ollama（推奨・最も簡単）

1. **Ollamaのインストール**
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.com/install.sh | sh
   
   # または https://ollama.com からダウンロード
   ```

2. **日本語対応モデルのダウンロード**
   ```bash
   # Qwen2.5 (推奨・日本語性能良好)
   ollama pull qwen2.5:14b
   
   # または Llama 3.1
   ollama pull llama3.1:8b
   
   # または Japanese Stable LM
   ollama pull stabilityai/japanese-stablelm-2-instruct-1.6b
   ```

3. **サーバー起動**
   ```bash
   ollama serve
   # デフォルトで http://localhost:11434 で起動
   ```

4. **.envファイル設定**
   ```bash
   OPENAI_API_BASE=http://localhost:11434/v1
   OPENAI_MODEL=qwen2.5:14b
   EMBEDDING_PROVIDER=huggingface
   EMBEDDING_MODEL=intfloat/multilingual-e5-large
   ```

### オプション2: LM Studio

1. **LM Studioのインストール**
   - https://lmstudio.ai からダウンロード

2. **モデルのダウンロード**
   - GUI内で以下のようなモデルを検索してダウンロード：
     - `TheBloke/Swallow-7B-Instruct-v0.1-GGUF`
     - `elyza/ELYZA-japanese-Llama-2-7b-fast-instruct-GGUF`

3. **Local Serverを起動**
   - LM Studio内で「Local Server」タブを開く
   - ポート: 1234（デフォルト）

4. **.envファイル設定**
   ```bash
   OPENAI_API_BASE=http://localhost:1234/v1
   OPENAI_MODEL=モデル名
   ```

## Embeddings設定

### HuggingFace Embeddings（推奨・無料）

```bash
# .env
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=intfloat/multilingual-e5-large
EMBEDDING_DEVICE=cpu  # GPUがある場合は "cuda"
```

**推奨モデル:**
- `intfloat/multilingual-e5-large` - 多言語対応、日本語性能良好（約1GB）
- `intfloat/multilingual-e5-base` - 軽量版（約500MB）
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` - 高速・軽量

## 動作確認

```bash
# サーバー起動
python app/main.py

# 別ターミナルでテスト
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "カタリナについて教えて"}'
```

## トラブルシューティング

### Embeddings モデルのダウンロードが遅い

初回起動時にHuggingFaceからモデルをダウンロードします（約1GB）。
キャッシュされるため2回目以降は高速です。

### GPUメモリ不足

```bash
# 軽量モデルに変更
EMBEDDING_MODEL=intfloat/multilingual-e5-base
EMBEDDING_DEVICE=cpu
```

### 日本語応答が不自然

- 日本語特化モデルを使用してください（Qwen2.5、Swallow等）
- プロンプトを調整してください（`app/agents/agent.py`の`SYSTEM_PROMPT`）

## パフォーマンス比較

| セットアップ | 応答速度 | 精度 | コスト | GPU要件 |
|------------|---------|------|--------|---------|
| Ollama + Qwen2.5:14b | 中 | 高 | 無料 | 推奨 |
| LM Studio | 中 | 中～高 | 無料 | 推奨 |
| vLLM | 高 | 高 | 無料 | 必須 |
| OpenAI API | 最高 | 最高 | 有料 | 不要 |
