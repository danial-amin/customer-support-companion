#!/usr/bin/env python3
"""
Script to add documents to RAG system.
Usage: python add_documents.py
"""

import requests
import json
import os
from pathlib import Path
from typing import List, Dict, Any

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")  # Optional if REQUIRE_API_KEY=false
INGEST_ENDPOINT = f"{API_BASE_URL}/api/v1/rag/ingest"


def ingest_document(
    text: str,
    source: str,
    metadata: Dict[str, Any] = None,
    namespace: str = None
) -> Dict[str, Any]:
    """Ingest a single document into RAG."""
    payload = {
        "text": text,
        "source": source,
        "metadata": metadata or {},
    }
    
    if namespace:
        payload["namespace"] = namespace
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    
    try:
        response = requests.post(INGEST_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "chunks_ingested": 0
        }


def ingest_file(file_path: str, category: str = "general", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Ingest a text file into RAG."""
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"File not found: {file_path}",
            "chunks_ingested": 0
        }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        file_metadata = {
            "category": category,
            "file_type": Path(file_path).suffix,
            "file_name": os.path.basename(file_path),
            **(metadata or {})
        }
        
        return ingest_document(
            text=text,
            source=os.path.basename(file_path),
            metadata=file_metadata
        )
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "chunks_ingested": 0
        }


def main():
    """Main function to add sample documents."""
    print("🚀 Adding documents to RAG system...")
    print(f"API URL: {API_BASE_URL}")
    print("-" * 60)
    
    # Sample documents
    documents = [
        {
            "text": """
            Return Policy
            
            We accept returns within 30 days of purchase. Items must be:
            - In original condition
            - With original tags attached
            - In original packaging
            
            Refunds will be processed within 5-7 business days after we receive the returned item.
            Shipping costs for returns are the responsibility of the customer unless the item is defective.
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
            
            Standard Shipping:
            - Delivery time: 5-7 business days
            - Cost: $5.99 (free on orders over $50)
            
            Express Shipping:
            - Delivery time: 2-3 business days
            - Cost: $12.99
            
            Overnight Shipping:
            - Delivery time: Next business day
            - Cost: $24.99
            
            International shipping available to select countries.
            """,
            "source": "shipping_info.md",
            "metadata": {
                "category": "policies",
                "type": "shipping"
            }
        },
        {
            "text": """
            Product Warranty
            
            All products come with a 1-year manufacturer warranty covering defects in materials and workmanship.
            
            Warranty Coverage:
            - Manufacturing defects
            - Component failures under normal use
            - Software issues (for applicable products)
            
            Warranty Exclusions:
            - Physical damage
            - Water damage
            - Unauthorized modifications
            - Normal wear and tear
            
            To claim warranty, contact support with your order number and a description of the issue.
            """,
            "source": "warranty_policy.md",
            "metadata": {
                "category": "policies",
                "type": "warranty"
            }
        },
        {
            "text": """
            Customer Support Hours
            
            Our support team is available:
            - Monday to Friday: 9 AM - 6 PM EST
            - Saturday: 10 AM - 4 PM EST
            - Sunday: Closed
            
            Contact Methods:
            - Email: support@example.com
            - Phone: 1-800-555-0123
            - Live Chat: Available on website during business hours
            
            Average response time:
            - Email: Within 24 hours
            - Phone: Immediate during business hours
            - Live Chat: Under 2 minutes
            """,
            "source": "support_hours.md",
            "metadata": {
                "category": "support",
                "type": "contact_info"
            }
        },
        {
            "text": """
            Product Specifications - Laptop Pro 15
            
            Display: 15.6-inch 4K UHD (3840 x 2160)
            Processor: Intel Core i7-12700H
            Memory: 16GB DDR4 RAM
            Storage: 512GB NVMe SSD
            Graphics: NVIDIA GeForce RTX 3060
            Battery: 83Wh, up to 8 hours
            Weight: 4.2 lbs
            Operating System: Windows 11 Pro
            
            Ports:
            - 2x USB-C (Thunderbolt 4)
            - 2x USB-A 3.2
            - 1x HDMI 2.1
            - 1x SD card reader
            - 1x 3.5mm headphone jack
            """,
            "source": "laptop_pro_15_specs.md",
            "metadata": {
                "category": "product_info",
                "product": "Laptop Pro 15",
                "type": "specifications"
            }
        }
    ]
    
    # Ingest documents
    results = []
    for doc in documents:
        print(f"\n📄 Ingesting: {doc['source']}")
        result = ingest_document(
            text=doc["text"],
            source=doc["source"],
            metadata=doc.get("metadata", {})
        )
        
        if result.get("success"):
            print(f"   ✅ Success! Ingested {result['chunks_ingested']} chunks")
        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    total_chunks = sum(r.get("chunks_ingested", 0) for r in results)
    successful = sum(1 for r in results if r.get("success"))
    failed = len(results) - successful
    
    print(f"Total documents: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total chunks ingested: {total_chunks}")
    
    if failed > 0:
        print("\n⚠️  Some documents failed to ingest. Check the errors above.")
    else:
        print("\n✅ All documents ingested successfully!")
        print("\n💡 Test the RAG system with:")
        print('   curl -X POST "http://localhost:8000/api/v1/query" \\')
        print('     -H "Content-Type: application/json" \\')
        print('     -d \'{"query": "What is your return policy?", "agent_type": "rag"}\'')


if __name__ == "__main__":
    main()

