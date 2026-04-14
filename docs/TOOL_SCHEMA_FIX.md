# ツールスキーマエラーの修正

## エラー内容

```json
{
    "detail": "1 validation error for Tool\nargs_schema\n  subclass of BaseModel expected"
}
```

## 原因

LangChainの新しいバージョンでは、`Tool`クラスではなく`StructuredTool`を使用する必要があります。

## 修正内容

### `app/agents/tools/search.py`

**修正前:**
```python
from langchain.tools import Tool

return Tool(
    name="search_knowledge",
    func=search_knowledge,
    args_schema=SearchInput,
)
```

**修正後:**
```python
from langchain.tools import StructuredTool

return StructuredTool(
    name="search_knowledge",
    func=search_knowledge,
    args_schema=SearchInput,
)
```

### Pydanticスキーマも修正

```python
class SearchInput(BaseModel):
    query: str = Field(..., description="...")
    element: Optional[str] = Field(default=None, ...)  # default=None を明示
    doc_type: Optional[str] = Field(default=None, ...)
    top_k: int = Field(default=5, ...)
```

## サーバー再起動

```bash
# Ctrl+C でサーバーを停止

# 再起動
python run.py

# または
run.bat
```

## 動作確認

```powershell
# チャットAPIテスト
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"message\": \"カタリナについて教えて\"}"
```

これでエージェントが正常に動作するはずです！
