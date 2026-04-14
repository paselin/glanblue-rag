"""
Search tool for LangChain agent.
"""
from typing import Optional, Dict, Any
from langchain.tools import Tool
from pydantic import BaseModel, Field

from app.rag.retriever import get_retriever
from app.core.logging import setup_logging

logger = setup_logging()


class SearchInput(BaseModel):
    """Input schema for search tool."""
    query: str = Field(..., description="検索クエリ（キャラクター名、武器名、攻略情報など）")
    element: Optional[str] = Field(None, description="属性フィルター（火、水、土、風、光、闇）")
    doc_type: Optional[str] = Field(None, description="ドキュメントタイプ（character, weapon, quest等）")
    top_k: Optional[int] = Field(5, description="取得する結果の数（デフォルト: 5）")


def search_knowledge(
    query: str,
    element: Optional[str] = None,
    doc_type: Optional[str] = None,
    top_k: int = 5,
) -> str:
    """
    グランブルーファンタジーの攻略情報を検索する。
    
    Args:
        query: 検索クエリ
        element: 属性フィルター（オプション）
        doc_type: ドキュメントタイプフィルター（オプション）
        top_k: 取得件数
        
    Returns:
        検索結果のテキスト
    """
    try:
        logger.info(f"Searching knowledge base: {query}")
        
        # Build filters
        filters = {}
        if element:
            filters["element"] = element
        if doc_type:
            filters["type"] = doc_type
        
        # Retrieve documents
        retriever = get_retriever()
        results = retriever.retrieve(
            query=query,
            top_k=top_k,
            filters=filters if filters else None,
        )
        
        if not results:
            return "検索結果が見つかりませんでした。別のキーワードで検索してみてください。"
        
        # Format results
        context = retriever.format_context(results)
        
        return context
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"検索中にエラーが発生しました: {str(e)}"


def create_search_tool() -> Tool:
    """Create search tool for agent."""
    return Tool(
        name="search_knowledge",
        description="""グランブルーファンタジーの攻略情報を検索するツール。
キャラクター情報、武器情報、編成、クエスト攻略などを検索できます。

使用例:
- "水属性のSSRキャラクター"
- "火属性の高難易度編成"
- "六竜攻略"
- "マグナ武器の評価"
""",
        func=search_knowledge,
        args_schema=SearchInput,
    )
