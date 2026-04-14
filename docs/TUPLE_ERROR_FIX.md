# タプルエラーの修正（追加）

## 新しい問題

```
AttributeError: 'tuple' object has no attribute 'metadata'
```

## 原因

`text_splitter.create_documents()`が期待される`List[Document]`ではなく、タプルを返している可能性があります。

## 修正内容

### 1. `app/services/indexer.py` - Document検証を追加

```python
# チャンク生成後に検証
validated_chunks = []
for chunk in chunks:
    if isinstance(chunk, LangchainDocument):
        validated_chunks.append(chunk)
    else:
        # タプルの場合は変換
        if isinstance(chunk, tuple) and len(chunk) == 2:
            validated_chunks.append(
                LangchainDocument(
                    page_content=chunk[0], 
                    metadata=chunk[1]
                )
            )
```

### 2. `app/rag/vector_store.py` - 追加のタプルチェック

```python
# タプルが混入していた場合の対処
if documents and isinstance(documents[0], tuple):
    documents = [doc[0] if isinstance(doc, tuple) else doc for doc in documents]
```

## 再実行

```bash
# Windowsで
set PYTHONPATH=%CD%
python scripts\setup_data.py
```

## デバッグ方法

エラーが続く場合は、以下で詳細を確認：

```python
# scripts/setup_data.py に追加
for i, chunk in enumerate(all_chunks[:3]):
    print(f"Chunk {i}: type={type(chunk)}")
    if hasattr(chunk, 'page_content'):
        print(f"  Content: {chunk.page_content[:50]}")
    if hasattr(chunk, 'metadata'):
        print(f"  Metadata: {chunk.metadata}")
```

これで解決するはずです！
