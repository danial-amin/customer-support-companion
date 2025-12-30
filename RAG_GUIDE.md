# RAG (Retrieval Augmented Generation) Guide

## Overview

The RAG system uses **hybrid search** combining:
1. **Semantic Search** (vector similarity) - Finds documents similar in meaning
2. **Keyword Search** - Finds documents containing specific keywords

This provides better results than either method alone.

## How It Works

### 1. Document Ingestion

Documents are:
- Split into chunks (1000 chars with 200 char overlap)
- Embedded using OpenAI embeddings
- Stored in Pinecone vector database

### 2. Hybrid Search

When you query:
1. Query is embedded (semantic)
2. Keywords are extracted from query
3. Both semantic and keyword scores are combined (70% semantic, 30% keyword)
4. Top results are returned

### 3. Answer Generation

LLM generates answer using retrieved context.

## Adding Documents to RAG

### Method 1: Using the API Endpoint

**Endpoint**: `POST /api/v1/rag/ingest`

**Request Body**:
```json
{
  "text": "Your document text here...",
  "source": "document_name.pdf",
  "metadata": {
    "category": "support",
    "version": "1.0"
  },
  "namespace": "optional_namespace"
}
```

**Example using curl**:
```bash
curl -X POST "http://localhost:8000/api/v1/rag/ingest" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "text": "Our return policy allows returns within 30 days of purchase. Items must be in original condition with tags attached.",
    "source": "return_policy.md",
    "metadata": {
      "category": "policies",
      "type": "return_policy"
    }
  }'
```

**Example using Python**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/rag/ingest",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": "your-api-key"
    },
    json={
        "text": "Your document text...",
        "source": "document.pdf",
        "metadata": {"category": "support"}
    }
)

print(response.json())
```

### Method 2: Using Python Script

Create a script to ingest multiple documents:

```python
from app.services.document_service import document_service

# Ingest a document
result = document_service.ingest_document(
    text="Your document text here...",
    source="document.pdf",
    metadata={"category": "support"}
)

print(f"Ingested {result['chunks_ingested']} chunks")
```

### Method 3: Batch Ingestion

```python
documents = [
    {"text": "Document 1 text...", "source": "doc1.pdf"},
    {"text": "Document 2 text...", "source": "doc2.pdf"},
    {"text": "Document 3 text...", "source": "doc3.pdf"},
]

for doc in documents:
    result = document_service.ingest_document(
        text=doc["text"],
        source=doc["source"]
    )
    print(f"Ingested {result['chunks_ingested']} chunks from {doc['source']}")
```

## Querying RAG

The RAG agent automatically uses hybrid search when you query:

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "query": "What is your return policy?",
    "agent_type": "rag"
  }'
```

## Hybrid Search Details

### How It Works

1. **Semantic Search**: Uses vector embeddings to find semantically similar content
2. **Keyword Extraction**: Extracts important keywords from the query
3. **Scoring**: Combines both scores:
   - `combined_score = 0.7 * semantic_score + 0.3 * keyword_score`

### Benefits

- **Better Recall**: Keyword search catches exact matches semantic search might miss
- **Better Precision**: Semantic search finds related content keyword search might miss
- **Flexible**: Works well for both specific queries and general questions

## Best Practices

### Document Preparation

1. **Clean Text**: Remove unnecessary formatting, headers, footers
2. **Structure**: Well-structured documents work better
3. **Length**: Documents are automatically chunked, but 1000-5000 words per document is ideal
4. **Metadata**: Add relevant metadata for filtering

### Metadata Usage

Use metadata to:
- Filter by category, type, date
- Track document sources
- Organize by department or topic

Example:
```json
{
  "text": "...",
  "metadata": {
    "category": "policies",
    "department": "customer_service",
    "date": "2024-01-15",
    "version": "2.0"
  }
}
```

### Query Tips

1. **Be Specific**: More specific queries get better results
2. **Use Keywords**: Include important terms in your query
3. **Natural Language**: The system understands natural language

## Monitoring

Check logs to see:
- How many chunks were ingested
- Which keywords were extracted
- How many context chunks were retrieved

## Troubleshooting

### No Results Returned

- Check if documents were ingested successfully
- Verify Pinecone connection
- Check if query matches document content

### Poor Results

- Add more relevant documents
- Improve document quality
- Adjust keyword_weight in hybrid search (default 0.3)

### Performance

- Use namespaces to organize documents
- Filter by metadata when querying
- Adjust chunk size if needed

## API Reference

### Ingest Document

**POST** `/api/v1/rag/ingest`

**Request**:
- `text` (required): Document text
- `source` (optional): Source identifier
- `metadata` (optional): Additional metadata
- `namespace` (optional): Pinecone namespace

**Response**:
- `success`: Boolean
- `chunks_ingested`: Number of chunks created
- `source`: Source identifier
- `error`: Error message if failed

### Query RAG

**POST** `/api/v1/query`

**Request**:
- `query`: Your question
- `agent_type`: "rag" (or "auto" for automatic routing)

**Response**:
- `answer`: Generated answer
- `agent_used`: "rag"
- `error`: Error if any

