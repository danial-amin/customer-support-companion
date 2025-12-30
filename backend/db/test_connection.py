#!/usr/bin/env python3
"""Test database connection and schema."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.database_service import database_service
from app.config import settings

def test_connection():
    """Test database connection."""
    print("Testing database connection...")
    print(f"Database URL configured: {settings.DATABASE_URL is not None or settings.DB_HOST is not None}")
    
    if not database_service.is_available():
        print("❌ Database service is not available")
        print("\nPlease check:")
        print("1. DATABASE_URL or DB_* environment variables are set")
        print("2. PostgreSQL container is running: docker-compose ps postgres")
        print("3. Database credentials are correct")
        return False
    
    print("✅ Database connection successful!")
    
    # Test schema
    print("\nFetching database schema...")
    schema = database_service.get_schema()
    
    if not schema:
        print("⚠️  No tables found in database")
        return False
    
    print(f"✅ Found {len(schema)} tables:")
    for table_name, table_info in schema.items():
        print(f"  - {table_name} ({len(table_info.get('columns', []))} columns)")
    
    # Test a simple query
    print("\nTesting a simple query...")
    try:
        result = database_service.execute_query("SELECT COUNT(*) as total FROM customers")
        if result and result.get('rows'):
            count = result['rows'][0].get('total', 0)
            print(f"✅ Query successful! Found {count} customers in database")
        else:
            print("⚠️  Query returned no results")
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

