"""Pinecone vector database service for RAG."""
from typing import List, Optional
import pinecone
from pinecone import Pinecone, ServerlessSpec
from app.config import settings
import logging
import re

logger = logging.getLogger(__name__)


class PineconeService:
    """Service for interacting with Pinecone vector database."""
    
    def __init__(self):
        self.pc: Optional[Pinecone] = None
        self.index = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Pinecone connection."""
        try:
            if not settings.PINECONE_API_KEY:
                logger.warning("Pinecone API key not set. RAG agent will not work.")
                return
            
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Check if index exists, create if not
            if settings.PINECONE_INDEX_NAME not in self.pc.list_indexes().names():
                logger.info(f"Creating Pinecone index: {settings.PINECONE_INDEX_NAME}")
                self.pc.create_index(
                    name=settings.PINECONE_INDEX_NAME,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
            
            self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
            logger.info("Pinecone initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            self.pc = None
            self.index = None
    
    def is_available(self) -> bool:
        """Check if Pinecone is available."""
        return self.index is not None
    
    def upsert_vectors(self, vectors: List[dict], namespace: Optional[str] = None):
        """Upsert vectors to Pinecone."""
        if not self.is_available():
            raise RuntimeError("Pinecone is not initialized")
        
        try:
            self.index.upsert(vectors=vectors, namespace=namespace)
            logger.info(f"Upserted {len(vectors)} vectors")
        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")
            raise
    
    def query(
        self,
        vector: List[float],
        top_k: int = 5,
        namespace: Optional[str] = None,
        filter: Optional[dict] = None
    ) -> List[dict]:
        """Query Pinecone for similar vectors."""
        if not self.is_available():
            raise RuntimeError("Pinecone is not initialized")
        
        try:
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=True
            )
            return results.get("matches", [])
        except Exception as e:
            logger.error(f"Error querying Pinecone: {e}")
            raise
    
    def hybrid_query(
        self,
        vector: List[float],
        keywords: List[str],
        top_k: int = 5,
        namespace: Optional[str] = None,
        filter: Optional[dict] = None,
        keyword_weight: float = 0.3
    ) -> List[dict]:
        """
        Hybrid search combining semantic (vector) and keyword search.
        
        Args:
            vector: Semantic embedding vector
            keywords: List of keywords for keyword matching
            top_k: Number of results to return
            namespace: Pinecone namespace
            filter: Metadata filter
            keyword_weight: Weight for keyword matching (0-1), rest is semantic
        
        Returns:
            Combined and re-ranked results
        """
        if not self.is_available():
            raise RuntimeError("Pinecone is not initialized")
        
        try:
            # Get more results for re-ranking
            semantic_results = self.index.query(
                vector=vector,
                top_k=top_k * 2,  # Get more for re-ranking
                namespace=namespace,
                filter=filter,
                include_metadata=True
            )
            
            matches = semantic_results.get("matches", [])
            
            # If no keywords, return semantic results
            if not keywords:
                return matches[:top_k]
            
            # Score results with keyword matching
            keyword_set = set([k.lower() for k in keywords])
            
            scored_results = []
            for match in matches:
                semantic_score = match.get("score", 0.0)
                text = match.get("metadata", {}).get("text", "").lower()
                
                # Count keyword matches
                text_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', text))
                keyword_matches = len(keyword_set.intersection(text_words))
                keyword_score = min(keyword_matches / max(len(keyword_set), 1), 1.0)
                
                # Combine scores
                combined_score = (1 - keyword_weight) * semantic_score + keyword_weight * keyword_score
                
                scored_results.append({
                    **match,
                    "score": combined_score,
                    "semantic_score": semantic_score,
                    "keyword_score": keyword_score
                })
            
            # Sort by combined score and return top_k
            scored_results.sort(key=lambda x: x["score"], reverse=True)
            return scored_results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in hybrid query: {e}")
            raise
    
    def delete_vectors(self, ids: List[str], namespace: Optional[str] = None):
        """Delete vectors from Pinecone."""
        if not self.is_available():
            raise RuntimeError("Pinecone is not initialized")
        
        try:
            self.index.delete(ids=ids, namespace=namespace)
            logger.info(f"Deleted {len(ids)} vectors")
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            raise


# Global instance
pinecone_service = PineconeService()

