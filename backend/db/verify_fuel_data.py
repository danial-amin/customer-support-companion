#!/usr/bin/env python3
"""Verify that the fuel management database has been initialized with data."""
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.database_service import database_service
from app.config import settings

def verify_database():
    """Verify database connection and data."""
    print("=" * 60)
    print("Fuel Management Database Verification")
    print("=" * 60)
    
    # Check if database is available
    if not database_service.is_available():
        print("❌ Database service is NOT available")
        print(f"   DB_HOST: {settings.DB_HOST}")
        print(f"   DB_NAME: {settings.DB_NAME}")
        print(f"   DB_USER: {settings.DB_USER}")
        return False
    
    print("✅ Database service is available")
    print()
    
    # Check for fuel management tables
    schema = database_service.get_schema()
    fuel_tables = [
        'fuel_types',
        'fuel_stations',
        'station_fuel_inventory',
        'vehicles',
        'fuel_cards',
        'fuel_transactions',
        'fuel_refills',
        'fuel_consumption_reports',
        'fuel_support_tickets'
    ]
    
    print("Checking for fuel management tables...")
    missing_tables = []
    for table in fuel_tables:
        if table in schema:
            print(f"  ✅ {table}")
        else:
            print(f"  ❌ {table} - MISSING")
            missing_tables.append(table)
    
    if missing_tables:
        print(f"\n❌ Missing {len(missing_tables)} table(s). Database may not be initialized.")
        return False
    
    print(f"\n✅ All {len(fuel_tables)} fuel management tables exist")
    print()
    
    # Check data counts
    print("Checking data counts...")
    queries = {
        'Fuel Types': 'SELECT COUNT(*) FROM fuel_types',
        'Fuel Stations': 'SELECT COUNT(*) FROM fuel_stations',
        'Station Inventory': 'SELECT COUNT(*) FROM station_fuel_inventory',
        'Vehicles': 'SELECT COUNT(*) FROM vehicles',
        'Fuel Cards': 'SELECT COUNT(*) FROM fuel_cards',
        'Fuel Transactions': 'SELECT COUNT(*) FROM fuel_transactions',
        'Fuel Refills': 'SELECT COUNT(*) FROM fuel_refills',
        'Consumption Reports': 'SELECT COUNT(*) FROM fuel_consumption_reports',
        'Support Tickets': 'SELECT COUNT(*) FROM fuel_support_tickets'
    }
    
    all_good = True
    for name, query in queries.items():
        try:
            result = database_service.execute_query(query)
            count = result['rows'][0]['count'] if result.get('rows') else 0
            if count > 0:
                print(f"  ✅ {name}: {count} record(s)")
            else:
                print(f"  ⚠️  {name}: {count} record(s) - NO DATA")
                all_good = False
        except Exception as e:
            print(f"  ❌ {name}: Error - {str(e)}")
            all_good = False
    
    print()
    
    # Sample data check
    print("Sample data verification...")
    try:
        # Check a sample station
        result = database_service.execute_query(
            "SELECT name, station_code, city FROM fuel_stations LIMIT 1"
        )
        if result.get('rows'):
            station = result['rows'][0]
            print(f"  ✅ Sample station: {station.get('name')} ({station.get('station_code')}) in {station.get('city')}")
        else:
            print("  ⚠️  No stations found")
            all_good = False
        
        # Check a sample transaction
        result = database_service.execute_query(
            "SELECT transaction_number, total_amount, transaction_date FROM fuel_transactions LIMIT 1"
        )
        if result.get('rows'):
            txn = result['rows'][0]
            print(f"  ✅ Sample transaction: {txn.get('transaction_number')} - €{txn.get('total_amount')} on {txn.get('transaction_date')}")
        else:
            print("  ⚠️  No transactions found")
            all_good = False
        
        # Check station sales aggregation
        result = database_service.execute_query(
            """SELECT fs.name, SUM(ft.total_amount) as total_sales
               FROM fuel_transactions ft
               JOIN fuel_stations fs ON ft.station_id = fs.id
               GROUP BY fs.id, fs.name
               ORDER BY total_sales DESC
               LIMIT 1"""
        )
        if result.get('rows'):
            top_station = result['rows'][0]
            print(f"  ✅ Top station by sales: {top_station.get('name')} with €{float(top_station.get('total_sales', 0)):.2f}")
        else:
            print("  ⚠️  Could not calculate station sales")
            all_good = False
            
    except Exception as e:
        print(f"  ❌ Error checking sample data: {str(e)}")
        all_good = False
    
    print()
    print("=" * 60)
    if all_good:
        print("✅ VERIFICATION PASSED - Database is properly initialized!")
    else:
        print("⚠️  VERIFICATION ISSUES - Some data may be missing")
    print("=" * 60)
    
    return all_good

if __name__ == "__main__":
    try:
        verify_database()
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

