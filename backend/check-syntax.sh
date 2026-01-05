#!/bin/bash
# Quick syntax check for all Python files
# This catches indentation errors and syntax issues before deployment

set -e

echo "🔍 Checking Python syntax in backend..."

ERRORS=0

# Check all Python files
for file in $(find app -name "*.py" -type f); do
    if ! python3 -m py_compile "$file" 2>&1; then
        echo "❌ Syntax error in: $file"
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $ERRORS -eq 0 ]; then
    echo "✅ All Python files have valid syntax!"
    exit 0
else
    echo "❌ Found $ERRORS file(s) with syntax errors"
    exit 1
fi

