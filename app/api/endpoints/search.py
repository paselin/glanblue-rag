"""
Search API endpoint.
"""
from typing import List

from fastapi import APIRouter, HTTPException

from app.models.schemas import SearchRequest, SearchResponse, SearchResult
from app.rag.retriever import get_retriever
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    """
    Search the Granblue Fantasy knowledge base.
    
    Args:
        request: Search request with query and filters
        
    Returns:
        Search results
    """
    try:
        logger.info(f"Received search request: {request.query}")
        
        # Build filters from request
        filters = {}
        if request.filters:
            if request.filters.type:
                filters["type"] = request.filters.type.value
            if request.filters.element:
                filters["element"] = request.filters.element.value
            if request.filters.rarity:
                filters["rarity"] = request.filters.rarity.value
        
        # Retrieve documents
        retriever = get_retriever()
        results = retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
            filters=filters if filters else None,
        )
        
        # Convert to response format
        search_results = []
        for doc, score in results:
            search_results.append(
                SearchResult(
                    id=doc.metadata.get("id", "unknown"),
                    type=doc.metadata.get("type", "unknown"),
                    name=doc.metadata.get("name", "N/A"),
                    content=doc.page_content,
                    metadata=doc.metadata,
                    score=float(score),
                )
            )
        
        response = SearchResponse(
            results=search_results,
            total=len(search_results),
            query=request.query,
        )
        
        logger.info(f"Search returned {len(search_results)} results")
        
        return response
        
    except Exception as e:
        logger.error(f"Search request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
