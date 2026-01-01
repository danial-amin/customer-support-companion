#!/bin/bash
# Railway setup script for database initialization
# This script can be run as a Railway deploy script

set -e

echo "🚀 Starting Railway database initialization..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable is not set"
    exit 1
fi

echo "📦 Installing psql client..."
apt-get update && apt-get install -y postgresql-client

echo "🔌 Connecting to database..."
echo "Database: $DATABASE_URL"

# Run initialization script
echo "📝 Running database initialization script..."
psql "$DATABASE_URL" -f backend/db/init_fuel_management.sql

echo "✅ Database initialization complete!"

# Verify tables were created
echo "🔍 Verifying database setup..."
psql "$DATABASE_URL" -c "\dt" || echo "⚠️  Warning: Could not list tables"

echo "✨ Setup complete!"

