# RAG Document Ingestion Guide

## Overview

The RAG (Retrieval Augmented Generation) system uses **Hybrid Search** which combines:
1. **Semantic Search** (70% weight) - Vector similarity using embeddings
2. **Keyword Search** (30% weight) - Exact keyword matching

This provides superior results compared to either method alone.

## How Hybrid Search Works

### 1. Document Processing
- Documents are split into chunks (1000 characters with 200 character overlap)
- Each chunk is embedded using OpenAI embeddings (1536 dimensions)
- Chunks are stored in Pinecone vector database with metadata

### 2. Query Processing
- Query is embedded (semantic search)
- Keywords are extracted from the query (keyword search)
- Both scores are combined: `combined_score = 0.7 * semantic_score + 0.3 * keyword_score`
- Top results are returned and used to generate the answer

### 3. Benefits
- **Better Recall**: Keyword search catches exact matches semantic might miss
- **Better Precision**: Semantic search finds related content keywords might miss
- **Flexible**: Works for both specific queries and general questions

## Adding Documents to RAG

### Method 1: Using the API Endpoint (Recommended)

**Endpoint**: `POST /api/v1/rag/ingest`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/rag/ingest" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "text": "Your document text here...",
    "source": "document_name.pdf",
    "metadata": {
      "category": "support",
      "type": "policy",
      "version": "1.0"
    },
    "namespace": "optional_namespace"
  }'
```

**Response**:
```json
{
  "success": true,
  "chunks_ingested": 5,
  "source": "document_name.pdf"
}
```

### Method 2: Using Python Script

Create a file `add_documents.py`:

```python
import requests
import json

API_URL = "http://localhost:8000/api/v1/rag/ingest"
API_KEY = "your-api-key"  # Optional if REQUIRE_API_KEY=false

documents = [
    {
        "text": """
        Return Policy
        
        We accept returns within 30 days of purchase. Items must be:
        - In original condition
        - With original tags attached
        - In original packaging
        
        Refunds will be processed within 5-7 business days.
        """,
        "source": "return_policy.md",
        "metadata": {
            "category": "policies",
            "type": "return_policy",
            "version": "2.0"
        }
    },
    {
        "text": """
        Shipping Information
        
        Standard shipping: 5-7 business days
        Express shipping: 2-3 business days
        Overnight shipping: Next business day
        
        Free shipping on orders over $50.
        """,
        "source": "shipping_info.md",
        "metadata": {
            "category": "policies",
            "type": "shipping"
        }
    }
]

for doc in documents:
    response = requests.post(
        API_URL,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        },
        json=doc
    )
    
    result = response.json()
    if result.get("success"):
        print(f"✅ Ingested {result['chunks_ingested']} chunks from {result['source']}")
    else:
        print(f"❌ Error: {result.get('error')}")
```

### Method 3: Batch Ingestion from Files

Create `ingest_files.py`:

```python
import requests
import os
from pathlib import Path

API_URL = "http://localhost:8000/api/v1/rag/ingest"
API_KEY = "your-api-key"

def ingest_file(file_path: str, category: str = "general"):
    """Ingest a text file into RAG."""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    response = requests.post(
        API_URL,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        },
        json={
            "text": text,
            "source": os.path.basename(file_path),
            "metadata": {
                "category": category,
                "file_type": Path(file_path).suffix
            }
        }
    )
    
    return response.json()

# Ingest multiple files
files = [
    ("documents/return_policy.txt", "policies"),
    ("documents/shipping_info.txt", "policies"),
    ("documents/product_guide.txt", "product_info"),
]

for file_path, category in files:
    if os.path.exists(file_path):
        result = ingest_file(file_path, category)
        print(f"{file_path}: {result}")
    else:
        print(f"File not found: {file_path}")
```

### Method 4: Using the Python Service Directly

```python
from app.services.document_service import document_service

# Ingest a document
result = document_service.ingest_document(
    text="Your document text here...",
    source="document.pdf",
    metadata={"category": "support", "type": "policy"},
    namespace="optional_namespace"
)

print(f"Ingested {result['chunks_ingested']} chunks")
```

## Verifying Hybrid Search

### Test Query

After ingesting documents, test the hybrid search:

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "query": "What is your return policy?",
    "agent_type": "rag"
  }'
```

### Check Logs

The backend logs will show:
- Extracted keywords from the query
- Number of context chunks retrieved
- Hybrid search is being used

```bash
docker logs customer-support-backend | grep -i "keyword\|hybrid\|context"
```

### Expected Behavior

1. **Semantic Search**: Finds documents similar in meaning (e.g., "return policy" finds "refund information")
2. **Keyword Search**: Finds documents with exact keywords (e.g., "return" matches "return policy")
3. **Combined**: Results are re-ranked by combined score

## Best Practices

### Document Preparation

1. **Clean Text**: Remove unnecessary formatting, headers, footers
2. **Structure**: Well-structured documents work better
3. **Length**: 1000-5000 words per document is ideal (auto-chunked)
4. **Metadata**: Add relevant metadata for filtering

### Metadata Usage

Use metadata to:
- Filter by category, type, date
- Track document sources
- Version control
- Organize by department/topic

Example:
```json
{
  "category": "support",
  "type": "policy",
  "department": "customer_service",
  "version": "2.0",
  "last_updated": "2024-03-01"
}
```

### Chunking Strategy

- **Chunk Size**: 1000 characters (default)
- **Overlap**: 200 characters (default)
- **Separators**: Paragraphs, sentences, words

Adjust if needed in `document_service.py`:
```python
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Adjust based on your needs
    chunk_overlap=200,     # Adjust overlap
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""]
)
```

## Troubleshooting

### Documents Not Found in Queries

1. **Check Pinecone**: Verify documents were ingested
   ```python
   # Check Pinecone index stats
   index_stats = pinecone_service.index.describe_index_stats()
   print(index_stats)
   ```

2. **Check Keywords**: Verify keyword extraction is working
   ```python
   keywords = document_service.extract_keywords("your query")
   print(keywords)
   ```

3. **Check Embeddings**: Verify embeddings are being created
   - Check backend logs for embedding errors
   - Verify OPENAI_API_KEY is set

### Hybrid Search Not Working

1. **Check Logs**: Look for "hybrid_query" in logs
2. **Verify Implementation**: Check `pinecone_service.hybrid_query()` is being called
3. **Test Separately**: Test semantic and keyword search independently

### Performance Issues

1. **Reduce Chunk Size**: Smaller chunks = more vectors = slower queries
2. **Use Namespaces**: Separate documents into namespaces
3. **Filter by Metadata**: Use metadata filters to narrow results

## Example: Complete Workflow

```bash
# 1. Add documents
curl -X POST "http://localhost:8000/api/v1/rag/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Return policy: 30 days, original condition required.",
    "source": "policy.md",
    "metadata": {"category": "policies"}
  }'

# 2. Query with RAG
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the return policy?",
    "agent_type": "rag"
  }'

# 3. Check logs
docker logs customer-support-backend | tail -20
```

## API Reference

### POST /api/v1/rag/ingest

**Request Body**:
```json
{
  "text": "string (required)",
  "source": "string (optional)",
  "metadata": {
    "key": "value"
  },
  "namespace": "string (optional)"
}
```

**Response**:
```json
{
  "success": true,
  "chunks_ingested": 5,
  "source": "document.pdf",
  "error": null
}
```

### Query Endpoint

Use the standard query endpoint with `agent_type: "rag"`:

```json
{
  "query": "your question",
  "agent_type": "rag"
}
```

The RAG agent automatically uses hybrid search!

