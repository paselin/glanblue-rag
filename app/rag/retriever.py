"""
RAG retriever implementation.
"""
from typing import List, Optional, Dict, Any
from langchain.schema import Document as LangchainDocument

from app.rag.vector_store import get_vector_store
from app.core.config import get_settings
from app.core.logging import setup_logging

logger = setup_logging()
settings = get_settings()


class Retriever:
    """Document retriever for RAG."""
    
    def __init__(self):
        """Initialize retriever."""
        self.vector_store = get_vector_store()
        self.top_k = settings.retrieval_top_k
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[LangchainDocument, float]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            filters: Metadata filters
            
        Returns:
            List of (document, score) tuples
        """
        k = top_k or self.top_k
        
        logger.info(f"Retrieving documents for query: {query[:50]}...")
        
        # Perform similarity search with scores
        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filters,
        )
        
        logger.info(f"Retrieved {len(results)} documents")
        
        return results
    
    def format_context(
        self,
        documents: List[tuple[LangchainDocument, float]],
        max_tokens: int = 3000,
    ) -> str:
        """
        Format retrieved documents into context string.
        
        Args:
            documents: List of (document, score) tuples
            max_tokens: Maximum tokens for context (approximation)
            
        Returns:
            Formatted context string
        """
        context_parts = []
        total_chars = 0
        max_chars = max_tokens * 4  # Rough approximation
        
        for doc, score in documents:
            doc_text = f"""
---
タイプ: {doc.metadata.get('type', 'unknown')}
名前: {doc.metadata.get('name', 'N/A')}
関連度: {score:.2f}

{doc.page_content}
---
"""
            if total_chars + len(doc_text) > max_chars:
                break
            
            context_parts.append(doc_text)
            total_chars += len(doc_text)
        
        return "\n".join(context_parts)


def get_retriever() -> Retriever:
    """Get retriever instance."""
    return Retriever()
