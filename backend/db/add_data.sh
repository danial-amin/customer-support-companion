#!/bin/bash
# Script to add more sample data to the database
# Usage: ./add_data.sh

set -e

# Get database connection details from environment or use defaults
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5433}
DB_NAME=${DB_NAME:-customersupport}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}

echo "Adding sample data to database..."
echo "Database: $DB_NAME"
echo "Host: $DB_HOST:$DB_PORT"
echo "User: $DB_USER"
echo ""

# Export password for psql
export PGPASSWORD=$DB_PASSWORD

# Run the SQL script
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$(dirname "$0")/add_sample_data.sql"

echo ""
echo "Sample data added successfully!"

