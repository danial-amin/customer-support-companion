# How to Get DATABASE_URL in Railway

Quick guide on getting the DATABASE_URL for your PostgreSQL container on Railway.

## For Docker Container PostgreSQL

When you deploy a PostgreSQL Docker container on Railway, you need to construct the DATABASE_URL manually.

### Step 1: Get Connection Details from PostgreSQL Service

1. Go to your **PostgreSQL service** in Railway
2. Click **"Variables"** tab
3. Note these values:
   - `POSTGRES_DB` (e.g., `customersupport`)
   - `POSTGRES_USER` (e.g., `postgres`)
   - `POSTGRES_PASSWORD` (the password you set)
   - Service name (e.g., `postgres` - shown at top of service)

### Step 2: Construct DATABASE_URL

Use this format:
```
postgresql://USERNAME:PASSWORD@SERVICE_NAME.railway.internal:PORT/DATABASE
```

**Example:**
```
postgresql://postgres:my-password-123@postgres.railway.internal:5432/customersupport
```

### Step 3: Set in Backend Service

1. Go to your **Backend service** → **"Variables"** tab
2. Add:
   ```
   DATABASE_URL=postgresql://postgres:your-password@postgres.railway.internal:5432/customersupport
   ```

## Finding Your Service Name

1. Go to Railway project dashboard
2. Look at your PostgreSQL service
3. The service name is shown at the top (e.g., `postgres`, `database`, etc.)
4. Use this name in the connection string: `SERVICE_NAME.railway.internal`

## Alternative: Using Individual Variables

Instead of `DATABASE_URL`, you can use:

```
DB_HOST=postgres.railway.internal
DB_PORT=5432
DB_NAME=customersupport
DB_USER=postgres
DB_PASSWORD=your-password-here
```

The application will automatically construct the connection string from these.

## Quick Reference

### Connection String Format

```
postgresql://USER:PASSWORD@HOST:PORT/DATABASE
```

### Railway Internal Host Format

```
SERVICE_NAME.railway.internal
```

**Examples:**
- Service named `postgres` → `postgres.railway.internal`
- Service named `database` → `database.railway.internal`
- Service named `pg` → `pg.railway.internal`

### Default Values

If you used the provided Dockerfile defaults:
- **User**: `postgres`
- **Database**: `customersupport`
- **Port**: `5432`
- **Password**: Whatever you set in `POSTGRES_PASSWORD`

## Step-by-Step Example

**PostgreSQL Service Variables:**
```
POSTGRES_DB=customersupport
POSTGRES_USER=postgres
POSTGRES_PASSWORD=abc123xyz
Service Name: postgres
```

**Backend Service DATABASE_URL:**
```
DATABASE_URL=postgresql://postgres:abc123xyz@postgres.railway.internal:5432/customersupport
```

## Troubleshooting

### Password Authentication Failed

**Error**: `FATAL: password authentication failed for user "postgres"`

**This means the password in your backend doesn't match the PostgreSQL service password.**

**Fix:**

1. **Go to PostgreSQL service** → **"Variables"** tab
2. **Check `POSTGRES_PASSWORD` value** - Copy it exactly
3. **Go to Backend service** → **"Variables"** tab
4. **Update `DATABASE_URL`** with the correct password:
   ```
   DATABASE_URL=postgresql://postgres:EXACT_PASSWORD_FROM_POSTGRES@postgres.railway.internal:5432/customersupport
   ```
5. **Or update individual variables:**
   ```
   DB_PASSWORD=EXACT_PASSWORD_FROM_POSTGRES
   ```
6. **Redeploy backend** (Railway auto-redeploys on variable change)

**💡 Common mistakes:**
- Password has special characters that need URL encoding
- Extra spaces in password
- Password changed in PostgreSQL but not updated in backend
- Using default password instead of the one you set

**URL Encoding Special Characters:**
If your password has special characters, encode them:
- `@` → `%40`
- `#` → `%23`
- `$` → `%24`
- `%` → `%25`
- `&` → `%26`
- `+` → `%2B`
- `=` → `%3D`

**Example:**
- Password: `my@pass#123`
- Encoded: `my%40pass%23123`
- URL: `postgresql://postgres:my%40pass%23123@postgres.railway.internal:5432/customersupport`

**Or use individual variables to avoid encoding:**
```
DB_HOST=postgres.railway.internal
DB_PORT=5432
DB_NAME=customersupport
DB_USER=postgres
DB_PASSWORD=my@pass#123  # No encoding needed!
```

### Can't Connect?

1. **Check service name matches:**
   - PostgreSQL service name: `postgres`
   - Use in URL: `postgres.railway.internal`

2. **Verify password matches:**
   - Check `POSTGRES_PASSWORD` in PostgreSQL service
   - Use exact same value in backend `DATABASE_URL`
   - **Copy-paste the password** to avoid typos

3. **Check port:**
   - Default is `5432`
   - Verify in PostgreSQL service settings if changed

4. **Verify database name:**
   - Check `POSTGRES_DB` in PostgreSQL service
   - Use exact same name in connection string

5. **Check username:**
   - Check `POSTGRES_USER` in PostgreSQL service
   - Usually `postgres` but verify

### Service Reference Not Working?

Railway's `${{postgres.DATABASE_URL}}` service references work for **managed services**, but may not work for custom Docker containers.

**Solution**: Construct the URL manually as shown above.

## Testing the Connection

After setting `DATABASE_URL`, check backend logs:

1. Go to Backend service → **"Logs"**
2. Look for:
   ```
   Database connection initialized
   Database configured: True
   ```

3. Test health endpoint:
   ```bash
   curl https://your-backend.railway.app/api/v1/health
   ```

4. Should return:
   ```json
   {
     "status": "healthy",
     "services": {
       "database": true
     }
   }
   ```

## Security Note

⚠️ **Never commit passwords to git!**

- Use Railway's environment variables
- Use strong passwords
- Rotate passwords regularly

