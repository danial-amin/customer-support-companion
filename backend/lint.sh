#!/bin/bash
# Lint the backend code
# Usage: ./lint.sh [--fix]

set -e

echo "🔍 Running Ruff linter on backend code..."

if [ "$1" == "--fix" ]; then
    echo "🔧 Auto-fixing issues..."
    ruff check --fix app/
else
    ruff check app/
fi

echo "✅ Linting complete!"

