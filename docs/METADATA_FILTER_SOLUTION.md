# メタデータフィルター問題の最終解決

## 根本原因

`langchain_community.vectorstores.utils.filter_complex_metadata` 関数が内部でタプルを処理する際にエラーが発生していました。

## 解決策

LangChainのフィルター関数を使わず、**独自のメタデータフィルター関数を実装**しました。

## 実装内容

### `app/rag/vector_store.py`

```python
def _filter_complex_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    ChromaDB互換のメタデータにフィルター。
    - プリミティブ型（str, int, float, bool）のみ許可
    - リストは文字列に変換
    - その他の複雑な型も文字列化
    """
    filtered = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            filtered[key] = value
        elif isinstance(value, list):
            # リストをカンマ区切り文字列に変換
            filtered[key] = ", ".join(str(v) for v in value)
        elif value is None:
            continue
        else:
            # その他は文字列化
            filtered[key] = str(value)
    return filtered
```

### 使用方法

```python
# 各Documentのメタデータをフィルター
for doc in validated_documents:
    filtered_metadata = _filter_complex_metadata(doc.metadata)
    filtered_doc = LangchainDocument(
        page_content=doc.page_content,
        metadata=filtered_metadata
    )
```

## 再実行

```bash
# Windowsで
set PYTHONPATH=%CD%
python scripts\setup_data.py
```

## 期待される結果

```
Processing 4 documents
Validating 4 chunks before indexing...
Adding 4 documents to vector store
Validated 4 documents
Successfully added 4 documents
Indexed 4 chunks from 4 documents
Setup complete! Indexed 4 chunks from 4 documents
```

これで完全に動作するはずです！🎉
