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
import io
from pathlib import Path

logger = logging.getLogger(__name__)

# File parsing imports
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyPDF2 not available. PDF parsing will be limited.")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("python-docx not available. DOCX parsing will be limited.")


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
    
    def parse_file(self, file_content: bytes, filename: str) -> str:
        """
        Parse file content based on file extension.
        
        Args:
            file_content: File content as bytes
            filename: Original filename (used to determine file type)
        
        Returns:
            Extracted text content
        """
        file_ext = Path(filename).suffix.lower()
        
        try:
            if file_ext == '.pdf':
                return self._parse_pdf(file_content)
            elif file_ext in ['.docx', '.doc']:
                return self._parse_docx(file_content)
            elif file_ext in ['.txt', '.md', '.csv']:
                return file_content.decode('utf-8', errors='ignore')
            else:
                # Try to decode as text
                return file_content.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Error parsing file {filename}: {e}")
            raise ValueError(f"Failed to parse file {filename}: {str(e)}")
    
    def _parse_pdf(self, file_content: bytes) -> str:
        """Parse PDF file content."""
        if not PDF_AVAILABLE:
            raise ValueError("PDF parsing not available. Please install PyPDF2.")
        
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_parts = []
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            return '\n\n'.join(text_parts)
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise
    
    def _parse_docx(self, file_content: bytes) -> str:
        """Parse DOCX file content."""
        if not DOCX_AVAILABLE:
            raise ValueError("DOCX parsing not available. Please install python-docx.")
        
        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)
            text_parts = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            return '\n\n'.join(text_parts)
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            raise
    
    def ingest_file(
        self,
        file_content: bytes,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parse and ingest a file into RAG.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            metadata: Additional metadata
            namespace: Pinecone namespace
        
        Returns:
            Dict with ingestion results
        """
        try:
            # Parse file to extract text
            text = self.parse_file(file_content, filename)
            
            if not text or not text.strip():
                return {
                    "success": False,
                    "error": "File appears to be empty or could not extract text",
                    "chunks_ingested": 0
                }
            
            # Prepare metadata
            file_metadata = {
                "file_type": Path(filename).suffix,
                "file_name": filename,
                **(metadata or {})
            }
            
            # Ingest using existing method
            return self.ingest_document(
                text=text,
                metadata=file_metadata,
                source=filename,
                namespace=namespace
            )
        except Exception as e:
            logger.error(f"Error ingesting file {filename}: {e}")
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

