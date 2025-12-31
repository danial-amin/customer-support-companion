#!/usr/bin/env python3
"""
Script to fix Pinecone index dimension mismatch.

This script checks the Pinecone index dimension and provides instructions
to fix dimension mismatches with embeddings.
"""

import os
import sys
from pinecone import Pinecone

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def main():
    """Check and fix Pinecone index dimension."""
    if not settings.PINECONE_API_KEY:
        print("❌ PINECONE_API_KEY not set in environment variables")
        return
    
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index_name = settings.PINECONE_INDEX_NAME
    
    print(f"Checking Pinecone index: {index_name}")
    print("-" * 60)
    
    # Check if index exists
    index_names = pc.list_indexes().names()
    if index_name not in index_names:
        print(f"✅ Index '{index_name}' does not exist. It will be created with correct dimension (1536) on first use.")
        return
    
    # Get index info
    try:
        index_info = pc.describe_index(index_name)
        actual_dimension = index_info.dimension
        expected_dimension = 1536  # text-embedding-ada-002 dimension
        
        print(f"Index dimension: {actual_dimension}")
        print(f"Expected dimension: {expected_dimension}")
        print("-" * 60)
        
        if actual_dimension == expected_dimension:
            print("✅ Index dimension is correct! No action needed.")
        else:
            print(f"❌ Dimension mismatch detected!")
            print(f"\nThe index has {actual_dimension} dimensions, but embeddings are {expected_dimension} dimensions.")
            print(f"\nTo fix this, you need to delete and recreate the index.")
            print(f"\n⚠️  WARNING: This will delete all existing vectors in the index!")
            
            response = input(f"\nDo you want to delete and recreate the index '{index_name}'? (yes/no): ")
            
            if response.lower() in ['yes', 'y']:
                print(f"\nDeleting index '{index_name}'...")
                pc.delete_index(index_name)
                print("✅ Index deleted.")
                
                print(f"\nCreating new index '{index_name}' with dimension {expected_dimension}...")
                from pinecone import ServerlessSpec
                pc.create_index(
                    name=index_name,
                    dimension=expected_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                print("✅ Index created successfully!")
                print("\nYou can now upload documents again.")
            else:
                print("\nIndex not modified. You'll need to fix the dimension mismatch manually.")
                print("\nAlternative: Use a different embedding model that produces 1024 dimensions.")
    
    except Exception as e:
        print(f"❌ Error checking index: {e}")
        return

if __name__ == "__main__":
    main()

