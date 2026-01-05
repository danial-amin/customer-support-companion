# Fix: Railway PostgreSQL SSL Connection Error

If you get `could not accept SSL connection: EOF detected` when connecting to Railway PostgreSQL, here's how to fix it.

## The Problem

Railway PostgreSQL requires SSL connections, but `psql` might not be using SSL by default, causing connection failures.

## Solutions

### Option 1: Add SSL Parameter to Connection String (Easiest)

```bash
# Get your DATABASE_URL from Railway
railway variables

# Connect with SSL required
psql "$DATABASE_URL?sslmode=require" -f backend/db/init_fuel_management.sql
```

### Option 2: Use Railway CLI (Recommended)

The easiest way is to use Railway's built-in connection:

```bash
railway connect postgres
```

This automatically handles SSL and connection details. Then you can paste your SQL:

```sql
\i backend/db/init_fuel_management.sql
```

Or copy-paste the contents of `init_fuel_management.sql` directly.

### Option 3: Set SSL Environment Variable

```bash
export PGSSLMODE=require
psql "$DATABASE_URL" -f backend/db/init_fuel_management.sql
```

### Option 4: Use Railway Web Interface (No SSL Issues)

1. Go to PostgreSQL service → **"Data"** tab
2. Click **"Query"**
3. Copy/paste contents of `backend/db/init_fuel_management.sql`
4. Click **"Run"**

This avoids SSL issues entirely!

## Common SSL Modes

- `sslmode=require` - Requires SSL (recommended for Railway)
- `sslmode=prefer` - Prefers SSL, falls back if not available
- `sslmode=disable` - No SSL (won't work with Railway)

## Troubleshooting

### Error: "could not accept SSL connection: EOF detected"

**Fix**: Add `?sslmode=require` to your connection string:
```bash
psql "$DATABASE_URL?sslmode=require" ...
```

### Error: "SSL connection required"

**Fix**: Railway requires SSL. Use one of the methods above.

### Error: "psql: error: connection to server failed"

**Check**:
1. Verify `DATABASE_URL` is correct
2. Ensure PostgreSQL service is running in Railway
3. Try using `railway connect postgres` instead

## Best Practice

For Railway deployments, use:
- **Railway CLI**: `railway connect postgres` (handles SSL automatically)
- **Web Interface**: Railway dashboard → Query tab (no SSL config needed)
- **Direct psql**: Add `?sslmode=require` to connection string

## Example Connection String Format

Railway's `DATABASE_URL` looks like:
```
postgresql://user:password@hostname:port/database
```

Add SSL parameter:
```
postgresql://user:password@hostname:port/database?sslmode=require
```

