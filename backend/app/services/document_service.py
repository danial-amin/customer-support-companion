"""Document processing service for RAG."""
from typing import List, Dict, Any, Optional
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # Fallback to simple splitter if package not available
    class RecursiveCharacterTextSplitter:
        def __init__(self, chunk_size=1000, chunk_overlap=200, length_function=len, separators=None):
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap
            self.length_function = length_function
            self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
        
        def split_text(self, text: str) -> List[str]:
            """Split text into chunks with overlap."""
            if self.length_function(text) <= self.chunk_size:
                return [text]
            
            chunks = []
            start = 0
            
            while start < len(text):
                end = start + self.chunk_size
                
                # Try to break at separators
                if end < len(text):
                    for sep in self.separators:
                        if sep:
                            sep_pos = text.rfind(sep, start, end)
                            if sep_pos != -1:
                                end = sep_pos + len(sep)
                                break
                
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                
                # Move start position with overlap
                start = max(end - self.chunk_overlap, start + 1)
                if start >= len(text):
                    break
            
            return chunks

from langchain_openai import OpenAIEmbeddings
from app.services.pinecone_service import pinecone_service
from app.config import settings
import logging
import uuid
import re

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for processing and ingesting documents into RAG."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def process_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Process a document: split into chunks and create embeddings.
        
        Args:
            text: The document text
            metadata: Additional metadata to attach to each chunk
            source: Source identifier (e.g., filename, URL)
        
        Returns:
            List of vectors ready for Pinecone upsert
        """
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Split document into {len(chunks)} chunks")
            
            # Create embeddings for all chunks
            embeddings = self.embeddings.embed_documents(chunks)
            
            # Prepare vectors for Pinecone
            vectors = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = str(uuid.uuid4())
                vector_metadata = {
                    "text": chunk,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "source": source or "unknown",
                    **(metadata or {})
                }
                
                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": vector_metadata
                })
            
            return vectors
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise
    
    def ingest_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest a document into Pinecone.
        
        Returns:
            Dict with ingestion results
        """
        try:
            if not pinecone_service.is_available():
                raise RuntimeError("Pinecone service is not available")
            
            # Process document
            vectors = self.process_document(text, metadata, source)
            
            # Upsert to Pinecone
            pinecone_service.upsert_vectors(vectors, namespace=namespace)
            
            return {
                "success": True,
                "chunks_ingested": len(vectors),
                "source": source or "unknown"
            }
        except Exception as e:
            logger.error(f"Error ingesting document: {e}")
            return {
                "success": False,
                "error": str(e),
                "chunks_ingested": 0
            }
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text for hybrid search.
        Simple keyword extraction - can be enhanced with NLP libraries.
        """
        # Remove common stop words and extract meaningful words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        # Extract words (alphanumeric, at least 3 chars)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter stop words and get unique keywords
        keywords = list(set([w for w in words if w not in stop_words]))
        
        # Return top keywords (by frequency or length)
        return sorted(keywords, key=lambda x: (text.lower().count(x), len(x)), reverse=True)[:20]


# Global instance
document_service = DocumentService()

