# Backend Linting Guide

This guide explains how to catch syntax and linting errors before they cause deployment issues.

## Quick Syntax Check (No Dependencies)

The fastest way to check for syntax errors (like indentation issues):

```bash
# From project root
make check-syntax

# Or directly
cd backend && ./check-syntax.sh
```

This catches:
- ✅ Indentation errors
- ✅ Syntax errors
- ✅ Import errors
- ✅ Basic Python issues

**Run this before committing or deploying!**

## Full Linting (With Ruff/Flake8)

For comprehensive linting (style, best practices, etc.):

### Install Linters

```bash
cd backend
pip install ruff flake8
```

### Run Linting

```bash
# Check for issues
make lint

# Auto-fix issues (where possible)
make lint-fix

# Or use ruff directly
ruff check app/
ruff check --fix app/  # Auto-fix
```

## Pre-Commit Check

Add this to your workflow before committing:

```bash
# Quick check
make check-syntax

# If that passes, commit
git add .
git commit -m "Your message"
```

## CI/CD Integration

Add to your deployment pipeline:

```yaml
# Example GitHub Actions
- name: Check Python syntax
  run: |
    cd backend
    find app -name "*.py" -exec python3 -m py_compile {} \;
```

## Common Issues Caught

1. **Indentation Errors** - Like the ones we just fixed
2. **Syntax Errors** - Missing colons, brackets, etc.
3. **Import Errors** - Missing or incorrect imports
4. **Unused Variables** - Dead code
5. **Style Issues** - Line length, spacing, etc.

## Why This Matters

- ✅ Catches errors before deployment
- ✅ Prevents Docker build failures
- ✅ Saves debugging time
- ✅ Maintains code quality

## Troubleshooting

If `make check-syntax` fails:
1. Read the error message
2. Fix the indicated file/line
3. Run again until it passes

If linters aren't installed:
- The basic syntax check still works
- Install ruff/flake8 for better checks: `pip install ruff flake8`

