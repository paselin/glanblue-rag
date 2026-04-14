# トラブルシューティングガイド

## 依存関係の問題

### PyTorch/Transformersのバージョン競合エラー

```
AttributeError: module 'torch.utils._pytree' has no attribute 'register_pytree_node'
```

**解決方法1: バージョンアップデート（推奨）**
```bash
pip install --upgrade torch transformers sentence-transformers
# または
pip install -r requirements.txt --force-reinstall
```

**解決方法2: OpenAI Embeddingsに切り替え（最も簡単）**

1. `.env`ファイルを編集:
```bash
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_API_KEY=sk-your-openai-key
```

2. 軽量版の依存関係を使用:
```bash
pip install -r requirements-light.txt
```

この方法ならPyTorchやTransformersは不要です。

**解決方法3: 仮想環境を再作成**
```bash
# 古い環境を削除
rm -rf venv  # Windows: rmdir /s venv

# 新しい環境を作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係を再インストール
pip install -r requirements.txt
```

## ChromaDB エラー

### "Collection not found"

```bash
# ベクトルDBを削除して再作成
rm -rf data/vector_db/*
python scripts/setup_data.py
```

### "Permission denied"

```bash
# データディレクトリの権限を確認
chmod -R 755 data/
```

## Playwright エラー

### "Browser not found"

```bash
# ブラウザを再インストール
playwright install chromium
```

## ローカルLLM接続エラー

### "Connection refused"

1. LLMサーバーが起動しているか確認:
```bash
# Ollamaの場合
curl http://localhost:11434/api/tags

# LM Studioの場合
curl http://localhost:1234/v1/models
```

2. `.env`のポート番号を確認

### "Model not found"

```bash
# Ollamaでモデルをダウンロード
ollama pull qwen2.5:14b

# モデル一覧を確認
ollama list
```

## Python バージョンエラー

Python 3.10以上が必要です:

```bash
python --version
# Python 3.10.0 以上であることを確認
```

## メモリ不足

### HuggingFace Embeddingsでメモリ不足

軽量モデルに変更:
```bash
EMBEDDING_MODEL=intfloat/multilingual-e5-base
```

または OpenAI Embeddings に切り替え:
```bash
EMBEDDING_PROVIDER=openai
```

## Windows特有の問題

### パスの区切り文字エラー

Windowsでは`\`ではなく`/`を使用するか、raw string を使用:
```python
CHROMA_PERSIST_DIR=./data/vector_db  # OK
CHROMA_PERSIST_DIR=.\\data\\vector_db  # OK
```

### 文字エンコーディングエラー

UTF-8を明示的に指定:
```bash
set PYTHONIOENCODING=utf-8
```

## よくある質問

### Q: Embeddingsは必須ですか？

A: はい、RAGシステムにはEmbeddingsが必須です。以下の選択肢があります：
- **OpenAI API**（有料・推奨）: 簡単で高精度
- **HuggingFace**（無料）: ローカルで動作、初回ダウンロードに時間がかかる

### Q: どのEmbeddingsを選べばいい？

A: 
- **初心者/手軽さ重視**: OpenAI Embeddings
- **完全無料/プライバシー重視**: HuggingFace Embeddings
- **コスト**: OpenAI約$0.0001/1000トークン、HuggingFaceは無料

### Q: GPUは必要ですか？

A: 
- **LLM**: ローカルLLM使用時は推奨（CPUでも動作するが遅い）
- **Embeddings**: OpenAI使用なら不要、HuggingFace使用なら推奨

## サポート

問題が解決しない場合は、以下を添えてIssueを作成してください：
- エラーメッセージ全文
- Python バージョン (`python --version`)
- OS情報
- `.env` の設定内容（APIキーは除く）
