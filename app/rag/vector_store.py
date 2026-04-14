"""
Vector store implementation using ChromaDB.
"""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain.schema import Document as LangchainDocument

from app.core.config import get_settings
from app.core.logging import setup_logging

logger = setup_logging()
settings = get_settings()


class VectorStore:
    """Vector store wrapper for ChromaDB."""
    
    def __init__(self):
        """Initialize vector store."""
        self.settings = settings
        self.embeddings = self._create_embeddings()
        self._vectorstore: Optional[Chroma] = None
    
    def _create_embeddings(self):
        """Create embeddings based on configuration."""
        if self.settings.embedding_provider == "openai":
            logger.info(f"Using OpenAI Embeddings: {self.settings.openai_embedding_model}")
            api_key = self.settings.openai_embedding_api_key or self.settings.openai_api_key
            return OpenAIEmbeddings(
                model=self.settings.openai_embedding_model,
                openai_api_key=api_key,
                openai_api_base=self.settings.openai_embedding_api_base,
            )
        else:
            logger.info(f"Using HuggingFace Embeddings: {self.settings.embedding_model}")
            return HuggingFaceEmbeddings(
                model_name=self.settings.embedding_model,
                model_kwargs={"device": self.settings.embedding_device},
                encode_kwargs={"normalize_embeddings": True},
            )
        
    def initialize(self):
        """Initialize ChromaDB connection."""
        try:
            logger.info(f"Initializing ChromaDB at {self.settings.chroma_persist_dir}")
            
            self._vectorstore = Chroma(
                collection_name=self.settings.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.settings.chroma_persist_dir,
            )
            
            logger.info("ChromaDB initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    @property
    def vectorstore(self) -> Chroma:
        """Get vector store instance."""
        if self._vectorstore is None:
            self.initialize()
        return self._vectorstore
    
    def add_documents(
        self,
        documents: List[LangchainDocument],
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add documents to vector store.
        
        Args:
            documents: List of documents to add
            ids: Optional list of document IDs
            
        Returns:
            List of added document IDs
        """
        try:
            logger.info(f"Adding {len(documents)} documents to vector store")
            
            # Filter complex metadata (lists, dicts, etc.)
            filtered_documents = [
                filter_complex_metadata(doc) for doc in documents
            ]
            
            result = self.vectorstore.add_documents(documents=filtered_documents, ids=ids)
            logger.info(f"Successfully added {len(result)} documents")
            return result
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[LangchainDocument]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Metadata filter
            
        Returns:
            List of similar documents
        """
        try:
            logger.info(f"Searching for: {query} (top_k={k})")
            results = self.vectorstore.similarity_search(
                query=query,
                k=k,
                filter=filter,
            )
            logger.info(f"Found {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[LangchainDocument, float]]:
        """
        Search with relevance scores.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Metadata filter
            
        Returns:
            List of (document, score) tuples
        """
        try:
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter,
            )
            return results
        except Exception as e:
            logger.error(f"Search with score failed: {e}")
            raise
    
    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents by IDs.
        
        Args:
            ids: List of document IDs to delete
        """
        try:
            logger.info(f"Deleting {len(ids)} documents")
            self.vectorstore.delete(ids=ids)
            logger.info("Documents deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            return {
                "name": self.settings.collection_name,
                "count": count,
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            raise


# Global instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
        _vector_store.initialize()
    return _vector_store
