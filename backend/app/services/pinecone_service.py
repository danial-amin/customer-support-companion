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
            
            # Expected dimension for OpenAI embeddings (text-embedding-ada-002)
            expected_dimension = 1536
            
            # Check if index exists
            index_names = self.pc.list_indexes().names()
            if settings.PINECONE_INDEX_NAME not in index_names:
                logger.info(f"Creating Pinecone index: {settings.PINECONE_INDEX_NAME} with dimension {expected_dimension}")
                self.pc.create_index(
                    name=settings.PINECONE_INDEX_NAME,
                    dimension=expected_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
            else:
                # Check existing index dimension
                try:
                    index_info = self.pc.describe_index(settings.PINECONE_INDEX_NAME)
                    actual_dimension = index_info.dimension
                    
                    if actual_dimension != expected_dimension:
                        logger.error(
                            f"Pinecone index dimension mismatch! "
                            f"Index has {actual_dimension} dimensions, but embeddings are {expected_dimension} dimensions. "
                            f"Please delete the index '{settings.PINECONE_INDEX_NAME}' and recreate it, or use an embedding model that produces {actual_dimension} dimensions."
                        )
                        # Don't raise error, just log it - let the user fix it
                        # The index will be None, so operations will fail gracefully
                        logger.warning("Pinecone index will not be used due to dimension mismatch")
                        self.pc = None
                        self.index = None
                        return
                    else:
                        logger.info(f"Pinecone index '{settings.PINECONE_INDEX_NAME}' has correct dimension: {actual_dimension}")
                except Exception as e:
                    logger.error(f"Error checking index dimension: {e}")
                    self.pc = None
                    self.index = None
                    return
            
            # Initialize the index connection
            try:
                self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
                logger.info("Pinecone initialized successfully")
            except Exception as e:
                logger.error(f"Error connecting to Pinecone index: {e}")
                self.index = None
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            self.pc = None
            self.index = None
    
    def is_available(self) -> bool:
        """Check if Pinecone is available."""
        return self.index is not None
    
    def _scored_vector_to_dict(self, scored_vector) -> dict:
        """Convert Pinecone ScoredVector to dictionary."""
        if isinstance(scored_vector, dict):
            return scored_vector
        
        # Handle ScoredVector object
        result = {
            "id": getattr(scored_vector, "id", None),
            "score": getattr(scored_vector, "score", 0.0),
            "metadata": getattr(scored_vector, "metadata", {}) or {},
            "values": getattr(scored_vector, "values", None)
        }
        return result
    
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
            matches = results.get("matches", [])
            # Convert ScoredVector objects to dictionaries
            return [self._scored_vector_to_dict(match) for match in matches]
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
            
            raw_matches = semantic_results.get("matches", [])
            # Convert ScoredVector objects to dictionaries
            matches = [self._scored_vector_to_dict(match) for match in raw_matches]
            
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

