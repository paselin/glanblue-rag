# Pydantic v2 互換性の問題と解決

## 問題

```
1 validation error for StructuredTool
args_schema
  subclass of BaseModel expected (type=type_error.subclass; expected_class=BaseModel)
```

## 原因

プロジェクトでPydantic v2を使用していますが、LangChainは内部でPydantic v1を使用しています。
`pydantic.BaseModel`を使うと、LangChainが期待する`pydantic.v1.BaseModel`と互換性がありません。

## 解決策

LangChainが提供する`pydantic_v1`を使用します。

### 修正内容

**修正前:**
```python
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    ...
```

**修正後:**
```python
from langchain.pydantic_v1 import BaseModel, Field

class SearchInput(BaseModel):
    ...
```

## サーバー再起動

```bash
# Windowsで
# Ctrl+C でサーバーを停止

python run.py
```

## 動作確認

```powershell
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"message\": \"カタリナについて教えて\"}"
```

## 補足: LangChainとPydanticのバージョン互換性

- **Pydantic v2**: 高速で新機能が豊富（プロジェクトで使用）
- **Pydantic v1**: LangChainが内部で使用
- **解決策**: LangChainは`langchain.pydantic_v1`で互換性レイヤーを提供

LangChainのツールやスキーマ定義では必ず`langchain.pydantic_v1`を使用してください。

## 他のファイルでの注意点

もし今後、他のツールやエージェントを追加する場合：

```python
# ❌ 間違い
from pydantic import BaseModel

# ✅ 正しい（LangChainのツール/スキーマ用）
from langchain.pydantic_v1 import BaseModel

# ✅ 正しい（FastAPIのスキーマ用）
from pydantic import BaseModel  # app/models/schemas.py など
```

使い分け:
- **LangChainのツール/エージェント**: `langchain.pydantic_v1`
- **FastAPI/アプリケーション**: `pydantic`（v2）
