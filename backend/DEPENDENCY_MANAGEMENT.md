# Dependency Management Strategy

## Problem
Using version ranges (e.g., `>=0.1.0`) in `requirements.txt` causes pip to spend significant time resolving dependencies, especially for the LangChain ecosystem which has many interdependent packages. This results in:
- Long Docker build times (5-10+ minutes)
- Inconsistent builds across environments
- Potential compatibility issues

## Solution
**Pin exact versions** for all dependencies using `==` instead of `>=`.

## Benefits

### 1. Faster Builds
- **Before**: pip spends 2-5 minutes resolving version ranges
- **After**: pip installs exact versions immediately (seconds)
- **Result**: Build time reduced by 60-80%

### 2. Reproducibility
- Same versions installed every time
- No surprises from dependency updates
- Consistent behavior across dev/staging/prod

### 3. Predictability
- Known working versions
- Easier debugging
- Clear upgrade path

## Current Pinned Versions

### LangChain Ecosystem
```
langchain==1.2.0
langchain-core==1.2.5
langchain-openai==1.1.6
langchain-community==0.4.1
langchain-text-splitters==1.1.0
langgraph==1.0.5
langgraph-checkpoint==3.0.1
openai==2.14.0
```

These versions are tested and work together.

### Other Dependencies
All major dependencies are pinned:
- `pydantic==2.12.5`
- `pandas==2.3.3`
- `matplotlib==3.10.8`
- `Office365-REST-Python-Client==2.6.2`
- etc.

## Updating Dependencies

When you need to update a package:

1. **Test locally first**:
   ```bash
   pip install package==new.version
   # Test your application
   ```

2. **Update requirements.txt**:
   ```bash
   # Change: package==old.version
   # To:     package==new.version
   ```

3. **Rebuild Docker image**:
   ```bash
   docker-compose build backend
   ```

4. **Test thoroughly** before committing

## Best Practices

1. **Always pin exact versions** in production
2. **Test updates** before committing
3. **Update dependencies regularly** (monthly/quarterly)
4. **Document breaking changes** when updating major versions
5. **Use virtual environments** for local development

## Verifying Versions

To check installed versions:
```bash
docker-compose exec backend pip freeze | grep langchain
```

To see what would be installed:
```bash
docker-compose exec backend pip install --dry-run -r requirements.txt
```

## Troubleshooting

If you encounter dependency conflicts:

1. Check if versions are compatible:
   ```bash
   pip check
   ```

2. Review error messages for conflicting packages

3. Update to compatible versions together (especially LangChain packages)

4. Consider using `pip-tools` for complex dependency management:
   ```bash
   pip install pip-tools
   pip-compile requirements.in
   ```

