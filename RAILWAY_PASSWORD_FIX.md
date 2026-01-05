# Fix: Password Authentication Failed on Railway

If you get `FATAL: password authentication failed for user "postgres"`, here's how to fix it.

## The Problem

The password in your backend service doesn't match the password set in your PostgreSQL service.

## Quick Fix

### Step 1: Get the Correct Password

1. Go to **PostgreSQL service** in Railway
2. Click **"Variables"** tab
3. Find `POSTGRES_PASSWORD`
4. **Copy the exact value** (click the copy icon or select and copy)

### Step 2: Update Backend Service

1. Go to **Backend service** → **"Variables"** tab
2. Find `DATABASE_URL` or create it
3. **Update with the correct password:**

   **Option A: Using DATABASE_URL**
   ```
   DATABASE_URL=postgresql://postgres:PASTE_PASSWORD_HERE@postgres.railway.internal:5432/customersupport
   ```
   
   **Option B: Using Individual Variables (Easier - No URL Encoding!)**
   ```
   DB_HOST=postgres.railway.internal
   DB_PORT=5432
   DB_NAME=customersupport
   DB_USER=postgres
   DB_PASSWORD=PASTE_PASSWORD_HERE
   ```

4. **Save** - Railway will auto-redeploy

### Step 3: Verify

1. Check backend logs → Should see "Database connection initialized"
2. Test health endpoint → Should return `"database": true`

## Common Issues

### Issue 1: Special Characters in Password

If your password has special characters like `@`, `#`, `$`, `%`, etc., they need URL encoding in `DATABASE_URL`.

**Solution**: Use individual variables instead:
```
DB_HOST=postgres.railway.internal
DB_PORT=5432
DB_NAME=customersupport
DB_USER=postgres
DB_PASSWORD=my@pass#123  # No encoding needed!
```

### Issue 2: Password Changed But Not Updated

If you changed the password in PostgreSQL service but didn't update the backend.

**Solution**: Update backend `DATABASE_URL` or `DB_PASSWORD` with the new password.

### Issue 3: Typo in Password

**Solution**: Copy-paste the password from PostgreSQL service to avoid typos.

### Issue 4: Wrong Username

**Error**: `password authentication failed for user "postgres"`

**Check**: Verify `POSTGRES_USER` in PostgreSQL service matches what you're using.

**Default**: Usually `postgres`, but verify in PostgreSQL service variables.

## Step-by-Step Fix

### Method 1: Using DATABASE_URL

1. **PostgreSQL service** → Variables → Copy `POSTGRES_PASSWORD`
2. **Backend service** → Variables → Update `DATABASE_URL`:
   ```
   postgresql://postgres:COPIED_PASSWORD@postgres.railway.internal:5432/customersupport
   ```
3. Wait for redeploy
4. Check logs

### Method 2: Using Individual Variables (Recommended)

1. **PostgreSQL service** → Variables → Note all values:
   - `POSTGRES_USER` (usually `postgres`)
   - `POSTGRES_PASSWORD` (copy this)
   - `POSTGRES_DB` (usually `customersupport`)

2. **Backend service** → Variables → Set:
   ```
   DB_HOST=postgres.railway.internal
   DB_PORT=5432
   DB_NAME=customersupport
   DB_USER=postgres
   DB_PASSWORD=COPIED_PASSWORD
   ```

3. **Remove `DATABASE_URL`** if you have it (individual variables take precedence)

4. Wait for redeploy
5. Check logs

## Verification

After fixing, verify the connection:

1. **Check Backend Logs:**
   ```
   Database connection initialized
   Database configured: True
   ```

2. **Test Health Endpoint:**
   ```bash
   curl https://your-backend.railway.app/api/v1/health
   ```
   
   Should return:
   ```json
   {
     "status": "healthy",
     "services": {
       "database": true
     }
   }
   ```

3. **If still failing:**
   - Double-check password is copied exactly
   - Verify service name matches (`postgres` → `postgres.railway.internal`)
   - Check PostgreSQL service is running
   - Check PostgreSQL logs for errors

## Best Practice

**Use individual variables instead of DATABASE_URL** to avoid URL encoding issues:

```
DB_HOST=postgres.railway.internal
DB_PORT=5432
DB_NAME=customersupport
DB_USER=postgres
DB_PASSWORD=your-password-here
```

This way:
- ✅ No URL encoding needed
- ✅ Easier to update password
- ✅ Less error-prone
- ✅ Application constructs URL automatically

## Still Not Working?

1. **Reset PostgreSQL password:**
   - Go to PostgreSQL service → Variables
   - Change `POSTGRES_PASSWORD` to a simple password (no special chars)
   - Update backend with new password
   - Redeploy both services

2. **Check PostgreSQL logs:**
   - Go to PostgreSQL service → Logs
   - Look for authentication errors
   - Verify database initialized correctly

3. **Verify service name:**
   - Check PostgreSQL service name in Railway
   - Use exact name: `SERVICE_NAME.railway.internal`

4. **Test connection manually:**
   - Use Railway's Query tab in PostgreSQL service
   - If that works, the issue is in backend configuration

