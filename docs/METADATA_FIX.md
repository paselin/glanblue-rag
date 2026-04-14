# メタデータエラーの修正

## 問題

ChromaDBはメタデータにリスト型を許可しません：
```
ValueError: Expected metadata value to be a str, int, float or bool, got ['初心者向け', 'サポート', '回復', 'ダメージカット']
```

## 修正内容

### 1. `app/services/indexer.py`

リスト型のメタデータ（`tags`）をカンマ区切り文字列に変換：

```python
# Before
metadata["tags"] = doc["tags"]  # ['tag1', 'tag2']

# After  
metadata["tags"] = ", ".join(doc["tags"])  # "tag1, tag2"
```

### 2. `app/rag/vector_store.py`

LangChainのフィルター関数を追加でメタデータをサニタイズ：

```python
from langchain_community.vectorstores.utils import filter_complex_metadata

# 複雑なメタデータを自動フィルター
filtered_documents = [
    filter_complex_metadata(doc) for doc in documents
]
```

## 再実行

```bash
# Windowsの場合
set PYTHONPATH=%CD%
python scripts\setup_data.py

# Linux/Macの場合
export PYTHONPATH=$(pwd)
python scripts/setup_data.py
```

これでエラーが解消されます！

## 変更されたメタデータの例

```python
# 元のデータ
{
    "tags": ["初心者向け", "サポート", "回復"],
    "element": "水"
}

# ChromaDBに保存される形式
{
    "tags": "初心者向け, サポート, 回復",
    "element": "水"
}
```

## 注意点

- タグは文字列として保存されますが、検索時は部分一致で機能します
- 配列として扱いたい場合は、検索時に `split(", ")` で復元できます
