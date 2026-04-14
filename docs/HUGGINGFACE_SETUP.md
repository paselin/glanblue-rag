# HuggingFace Embeddings セットアップ手順

## 1. 依存関係のインストール

```bash
# 仮想環境をアクティベート
source venv/bin/activate  # Windows: venv\Scripts\activate

# requirements.txtのインストール
pip install -r requirements.txt

# または個別にインストール
pip install sentence-transformers==2.7.0 torch==2.3.0 transformers==4.40.0
```

## 2. .env ファイルの設定

```bash
cp .env.example .env
```

`.env`を開いて以下を確認：

```bash
# HuggingFace Embeddingsを使用
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=intfloat/multilingual-e5-large
EMBEDDING_DEVICE=cpu  # GPUがある場合は "cuda"
```

## 3. モデルの選択

### 推奨モデル（日本語対応）

| モデル名 | サイズ | 速度 | 精度 | 用途 |
|---------|-------|------|------|------|
| `intfloat/multilingual-e5-large` | 1.1GB | 中 | 高 | **推奨・バランス型** |
| `intfloat/multilingual-e5-base` | 560MB | 速 | 中 | 軽量版 |
| `intfloat/multilingual-e5-small` | 470MB | 最速 | 中 | 最軽量 |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | 470MB | 速 | 中 | 高速版 |

### メモリ/速度が心配な場合

```bash
# 軽量モデルに変更
EMBEDDING_MODEL=intfloat/multilingual-e5-base
```

## 4. 初回起動（モデルダウンロード）

```bash
# データセットアップを実行
python scripts/setup_data.py
```

**初回のみ**: HuggingFaceから自動的にモデルをダウンロードします。
- 時間: 約5-10分（回線速度による）
- 保存場所: `~/.cache/huggingface/`
- 2回目以降: キャッシュから読み込むため高速

## 5. GPU使用（オプション）

GPUがある場合、高速化できます：

```bash
# .env
EMBEDDING_DEVICE=cuda

# CUDAがインストールされているか確認
python -c "import torch; print(torch.cuda.is_available())"
# True なら GPU使用可能
```

## 6. 動作確認

```bash
# サーバー起動
python app/main.py

# 別ターミナルでテスト
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "カタリナ",
    "top_k": 3
  }'
```

## トラブルシューティング

### エラー: "No module named 'sentence_transformers'"

```bash
pip install sentence-transformers==2.7.0
```

### エラー: PyTorchバージョン競合

```bash
# 仮想環境を再作成
rm -rf venv  # Windows: rmdir /s venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### ダウンロードが遅い/失敗する

```bash
# 軽量モデルに変更
EMBEDDING_MODEL=intfloat/multilingual-e5-base

# または手動ダウンロード
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-large')"
```

### メモリ不足エラー

```bash
# 小さいモデルを使用
EMBEDDING_MODEL=intfloat/multilingual-e5-small
```

### Windows特有の問題

```bash
# UTF-8エンコーディングを設定
set PYTHONIOENCODING=utf-8

# 長いパス名を有効化（Windows 10以降）
reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1
```

## パフォーマンス比較

### CPUでのベンチマーク（参考値）

| モデル | 初回起動時間 | Embedding生成速度 | メモリ使用量 |
|--------|-------------|------------------|--------------|
| e5-large | 2-3分 | ~50 docs/sec | ~2GB |
| e5-base | 1-2分 | ~100 docs/sec | ~1GB |
| e5-small | 1分 | ~150 docs/sec | ~800MB |

### GPUでのベンチマーク（CUDA）

| モデル | Embedding生成速度 | VRAM使用量 |
|--------|------------------|------------|
| e5-large | ~500 docs/sec | ~2GB |
| e5-base | ~800 docs/sec | ~1GB |
| e5-small | ~1000 docs/sec | ~800MB |

## キャッシュの管理

### キャッシュ場所

```bash
# Linux/Mac
~/.cache/huggingface/

# Windows
C:\Users\<username>\.cache\huggingface\
```

### キャッシュを削除（再ダウンロードが必要）

```bash
# Linux/Mac
rm -rf ~/.cache/huggingface/

# Windows
rmdir /s %USERPROFILE%\.cache\huggingface
```

## 次のステップ

セットアップ完了後：
1. サンプルデータでテスト
2. Wiki スクレイピング実装
3. 本番データでインデックス作成

問題があれば [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) を参照してください。
