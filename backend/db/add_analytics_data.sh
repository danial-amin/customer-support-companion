#!/bin/bash
# Script to add comprehensive analytics data to the database
# Usage: ./add_analytics_data.sh

set -e

# Get database connection details from environment or use defaults
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5433}
DB_NAME=${DB_NAME:-customersupport}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}

echo "Adding comprehensive analytics data to database..."
echo "Database: $DB_NAME"
echo "Host: $DB_HOST:$DB_PORT"
echo "User: $DB_USER"
echo ""

# Export password for psql
export PGPASSWORD=$DB_PASSWORD

# Run the SQL script
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$(dirname "$0")/add_analytics_data.sql"

echo ""
echo "Analytics data added successfully!"
echo ""
echo "Summary:"
echo "- 20 additional customers"
echo "- 15 additional products"
echo "- 50 orders across 5 months (Nov 2023 - Mar 2024)"
echo "- Multiple order items per order"
echo "- 40+ support tickets with detailed information"

