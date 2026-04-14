"""
Document indexer for processing and storing scraped data.
"""
from typing import List, Dict, Any
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document as LangchainDocument

from app.rag.vector_store import get_vector_store
from app.core.config import get_settings
from app.core.logging import setup_logging

logger = setup_logging()
settings = get_settings()


class DocumentIndexer:
    """Index documents into vector store."""
    
    def __init__(self):
        """Initialize indexer."""
        self.vector_store = get_vector_store()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "、", " ", ""],
        )
    
    def process_and_index(self, documents: List[Dict[str, Any]]) -> int:
        """
        Process and index documents.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Number of indexed chunks
        """
        logger.info(f"Processing {len(documents)} documents")
        
        all_chunks = []
        all_ids = []
        
        for doc in documents:
            chunks = self._process_document(doc)
            
            # Debug: Check chunk types
            for i, chunk in enumerate(chunks):
                logger.debug(f"Chunk {i} type: {type(chunk)}")
                if not isinstance(chunk, LangchainDocument):
                    logger.error(f"Invalid chunk type detected: {type(chunk)}")
                    logger.error(f"Chunk content: {chunk}")
            
            all_chunks.extend(chunks)
            
            # Generate IDs
            base_id = doc.get("id", f"{doc['type']}_{doc['name']}")
            chunk_ids = [f"{base_id}_chunk_{i}" for i in range(len(chunks))]
            all_ids.extend(chunk_ids)
        
        # Final validation before adding to vector store
        logger.info(f"Validating {len(all_chunks)} chunks before indexing...")
        validated_chunks = []
        for i, chunk in enumerate(all_chunks):
            if isinstance(chunk, LangchainDocument):
                validated_chunks.append(chunk)
            else:
                logger.warning(f"Chunk {i} is not a Document: {type(chunk)}")
                # Attempt conversion
                if isinstance(chunk, tuple) and len(chunk) == 2:
                    logger.info(f"Converting tuple to Document at index {i}")
                    validated_chunks.append(
                        LangchainDocument(page_content=chunk[0], metadata=chunk[1])
                    )
                elif isinstance(chunk, dict) and 'page_content' in chunk and 'metadata' in chunk:
                    logger.info(f"Converting dict to Document at index {i}")
                    validated_chunks.append(
                        LangchainDocument(page_content=chunk['page_content'], metadata=chunk['metadata'])
                    )
                else:
                    logger.error(f"Cannot convert chunk at index {i}: {chunk}")
        
        # Add to vector store
        if validated_chunks:
            self.vector_store.add_documents(validated_chunks, ids=all_ids[:len(validated_chunks)])
            logger.info(f"Indexed {len(validated_chunks)} chunks from {len(documents)} documents")
        
        return len(validated_chunks)
    
    def _process_document(self, doc: Dict[str, Any]) -> List[LangchainDocument]:
        """
        Process a single document into chunks.
        
        Args:
            doc: Document dictionary
            
        Returns:
            List of document chunks
        """
        # Create formatted content
        formatted_content = self._format_content(doc)
        
        # Create metadata
        metadata = self._create_metadata(doc)
        
        # Split into chunks
        chunks = self.text_splitter.create_documents(
            texts=[formatted_content],
            metadatas=[metadata],
        )
        
        # Ensure all chunks are Document objects
        validated_chunks = []
        for chunk in chunks:
            if isinstance(chunk, LangchainDocument):
                validated_chunks.append(chunk)
            else:
                logger.warning(f"Invalid chunk type: {type(chunk)}, converting...")
                # Convert to Document if needed
                if isinstance(chunk, tuple) and len(chunk) == 2:
                    validated_chunks.append(LangchainDocument(page_content=chunk[0], metadata=chunk[1]))
                else:
                    logger.error(f"Cannot convert chunk: {chunk}")
        
        return validated_chunks
    
    def _format_content(self, doc: Dict[str, Any]) -> str:
        """Format document content."""
        parts = []
        
        # Add title
        if "name" in doc:
            parts.append(f"# {doc['name']}\n")
        
        # Add basic info
        if doc.get("element"):
            parts.append(f"属性: {doc['element']}")
        if doc.get("rarity"):
            parts.append(f"レアリティ: {doc['rarity']}")
        
        parts.append("")  # Blank line
        
        # Add main content
        if "content" in doc:
            parts.append(doc["content"])
        
        return "\n".join(parts)
    
    def _create_metadata(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Create metadata for document."""
        metadata = {
            "type": doc.get("type", "unknown"),
            "name": doc.get("name", "N/A"),
            "updated_at": datetime.now().isoformat(),
        }
        
        # Add optional fields
        for field in ["element", "rarity", "tier", "source_url"]:
            if field in doc:
                metadata[field] = doc[field]
        
        # Convert list fields to comma-separated strings
        if "tags" in doc and doc["tags"]:
            metadata["tags"] = ", ".join(doc["tags"]) if isinstance(doc["tags"], list) else doc["tags"]
        
        return metadata


def get_indexer() -> DocumentIndexer:
    """Get indexer instance."""
    return DocumentIndexer()
