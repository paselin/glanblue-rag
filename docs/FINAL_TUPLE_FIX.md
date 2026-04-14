# タプルエラー徹底修正

## 問題の根本原因

`text_splitter.create_documents()` が想定外の形式（タプルなど）を返している。

## 実施した修正

### 1. 多段階の検証を追加

**`app/services/indexer.py`**:
- `_process_document()` 内で検証（既存）
- `process_and_index()` 内で**全チャンクを再検証**
- タプル・辞書からDocumentへの変換ロジック強化

**`app/rag/vector_store.py`**:
- `add_documents()` 内でさらに検証
- `filter_complex_metadata()` 実行前に必ずDocument型を保証

### 2. デバッグログを有効化

`.env` または `app/core/config.py`:
```python
LOG_LEVEL=DEBUG
```

これでチャンクの型情報が詳細にログ出力されます。

## 再実行手順

```bash
# Windowsで
set PYTHONPATH=%CD%
python scripts\setup_data.py
```

## 期待されるログ出力

成功時:
```
Processing 4 documents
Chunk 0 type: <class 'langchain.schema.document.Document'>
Validating 4 chunks before indexing...
Document 0 type: <class 'langchain.schema.document.Document'>, is LangchainDocument: True
Validated 4 documents
Successfully added 4 documents
```

エラー時（詳細な型情報が出力される）:
```
Chunk 0 type: <class 'tuple'>
Chunk content: ('text content', {'metadata': 'value'})
Converting tuple to Document at index 0
```

## それでもエラーが出る場合

`text_splitter` 自体に問題がある可能性があります。以下を試してください：

### オプション1: 手動でDocumentを作成

`app/services/indexer.py` の `_process_document()` を変更:

```python
def _process_document(self, doc: Dict[str, Any]) -> List[LangchainDocument]:
    formatted_content = self._format_content(doc)
    metadata = self._create_metadata(doc)
    
    # text_splitterを使わずに手動で作成
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    
    # テキストを分割
    text_chunks = splitter.split_text(formatted_content)
    
    # 手動でDocumentオブジェクトを作成
    documents = [
        LangchainDocument(page_content=chunk, metadata=metadata.copy())
        for chunk in text_chunks
    ]
    
    return documents
```

この修正を試してみてください！
