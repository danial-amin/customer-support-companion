# Deploying PostgreSQL Docker Container on Railway

This guide shows you how to deploy your own PostgreSQL container on Railway (instead of Railway's managed service) that auto-initializes with your schema.

## Overview

You'll deploy:
1. **PostgreSQL container** - Your own Docker-based PostgreSQL service
2. **Backend service** - Your FastAPI application
3. **Frontend service** - Your React application (optional)

The PostgreSQL container will automatically initialize with your schema when it starts.

## Step-by-Step Setup

### Step 1: Create Railway Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository

### Step 2: Deploy PostgreSQL Container

1. In Railway project, click **"+ New"**
2. Select **"GitHub Repo"** → Choose your repository
3. Railway will try to auto-detect - we need to configure it manually

**Configure PostgreSQL Service:**

1. Click on the service → **"Settings"** tab
2. Configure:
   - **Name**: `postgres` (or `database`)
   - **Root Directory**: Leave empty (or `backend/db` if you want)
   - **Dockerfile Path**: We'll create one
   - **Start Command**: Leave empty (handled by Dockerfile)

### Step 3: Use the Provided PostgreSQL Dockerfile

I've already created `backend/db/Dockerfile.postgres` for you! It:
- ✅ Uses PostgreSQL 15 Alpine (lightweight)
- ✅ Auto-initializes with `init_fuel_management.sql`
- ✅ Sets sensible defaults
- ✅ Can be customized via environment variables

**The Dockerfile is ready to use!** No need to create it.

### Step 4: Configure PostgreSQL Service in Railway

1. Go to PostgreSQL service → **"Settings"**
2. Set:
   - **Root Directory**: `backend/db`
   - **Dockerfile Path**: `Dockerfile.postgres` (relative to root directory)
   
   **💡 Note**: Since Root Directory is `backend/db`, Railway will look for `Dockerfile.postgres` in that directory, which is correct!

3. **Add Environment Variables:**
   ```
   POSTGRES_DB=customersupport
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your-strong-password-here
   ```

   **Generate a strong password:**
   ```bash
   openssl rand -base64 32
   ```

   **💡 Important**: The database will automatically initialize with your schema (`init_fuel_management.sql`) on first start!

### Step 5: Deploy Backend Service

1. Click **"+ New"** → **"GitHub Repo"** → Select repository
2. Configure:
   - **Root Directory**: `backend`
   - **Dockerfile Path**: `Dockerfile`

3. **Add Environment Variables:**
   
   **First, get the connection details from your PostgreSQL service:**
   
   **Method 1: Using Railway Service References (if available)**
   ```
   DATABASE_URL=${{postgres.DATABASE_URL}}
   ```
   
   **Method 2: Manual Construction (Recommended for Docker containers)**
   
   Go to your **PostgreSQL service** → **"Variables"** tab and note:
   - Service name (e.g., `postgres`)
   - Your environment variables: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
   
   Then in **Backend service** → **"Variables"**, set:
   ```
   OPENAI_API_KEY=your-openai-key
   SECRET_KEY=your-secret-key
   
   # Construct DATABASE_URL manually
   DATABASE_URL=postgresql://postgres:your-password@postgres.railway.internal:5432/customersupport
   ```
   
   **Or use individual variables (Recommended - avoids URL encoding issues):**
   ```
   DB_HOST=postgres.railway.internal
   DB_PORT=5432
   DB_NAME=customersupport
   DB_USER=postgres
   DB_PASSWORD=your-password-from-postgres-service
   ```
   
   **💡 Important**: 
   - Copy the password **exactly** from PostgreSQL service `POSTGRES_PASSWORD`
   - If password has special characters, use individual variables (no URL encoding needed)
   - Service name must match: if PostgreSQL service is named `postgres`, use `postgres.railway.internal`
   
   **💡 Important**: 
   - Use `postgres.railway.internal` as the host (Railway's internal DNS)
   - Or use your service name: `your-service-name.railway.internal`
   - Port is usually `5432`
   - Use the same values you set in PostgreSQL service environment variables

### Step 6: Generate Public URLs

1. **PostgreSQL service**: Usually doesn't need a public URL (internal only)
2. **Backend service**: Generate domain → Copy URL
3. **Frontend service** (if deploying): Generate domain → Copy URL

### Step 7: Verify Database Initialization

1. Go to PostgreSQL service → **"Logs"** tab
2. Look for:
   ```
   /usr/local/bin/docker-entrypoint.sh: running /docker-entrypoint-initdb.d/init_fuel_management.sql
   ```
3. Check for any SQL errors in the logs

### Step 8: Test Connection

1. Go to backend service → **"Logs"** tab
2. Look for:
   ```
   Database connection initialized
   Database configured: True
   ```
3. Test health endpoint:
   ```bash
   curl https://your-backend.railway.app/api/v1/health
   ```
4. Should return: `{"status": "healthy", "services": {"database": true}}`

## Alternative: Using docker-compose.yml on Railway

Railway doesn't directly support docker-compose, but you can use a similar approach:

### Option A: Separate Services (Recommended)

Deploy PostgreSQL and Backend as separate Railway services (as described above).

### Option B: Custom Dockerfile with Both Services

Create a Dockerfile that runs both PostgreSQL and your backend (not recommended for production, but works):

```dockerfile
# This is a workaround - not ideal for production
FROM docker:latest

# Install docker-compose
RUN apk add --no-cache docker-compose

# Copy docker-compose.yml
COPY docker-compose.yml .

# Start services
CMD ["docker-compose", "up"]
```

**Note**: This requires Docker-in-Docker which Railway may not support well.

## Getting DATABASE_URL for Docker Container

**⚠️ Important**: Railway service references (`${{postgres.DATABASE_URL}}`) work for **managed services**, but may NOT work for custom Docker containers.

### How to Get DATABASE_URL

1. **Go to PostgreSQL service** → **"Variables"** tab
2. **Note these values:**
   - Service name (shown at top, e.g., `postgres`)
   - `POSTGRES_DB` (e.g., `customersupport`)
   - `POSTGRES_USER` (e.g., `postgres`)
   - `POSTGRES_PASSWORD` (your password)

3. **Construct DATABASE_URL:**
   ```
   postgresql://USER:PASSWORD@SERVICE_NAME.railway.internal:5432/DATABASE
   ```

4. **Example:**
   ```
   postgresql://postgres:my-password@postgres.railway.internal:5432/customersupport
   ```

5. **Set in Backend service** → **"Variables"**:
   ```
   DATABASE_URL=postgresql://postgres:your-password@postgres.railway.internal:5432/customersupport
   ```

**💡 Quick Reference:** See [RAILWAY_GET_DATABASE_URL.md](./RAILWAY_GET_DATABASE_URL.md) for detailed instructions.

### Service References (May Not Work for Docker Containers)

Railway service references work like this:

```
${{SERVICE_NAME.VARIABLE_NAME}}
```

**Note**: These work for Railway's managed services, but custom Docker containers may not expose these variables automatically.

**If service references don't work**, construct the URL manually as shown above.

## Database Initialization

### How It Works

1. PostgreSQL container starts
2. If database is empty, it runs scripts in `/docker-entrypoint-initdb.d/`
3. Your `init_fuel_management.sql` runs automatically
4. Database is ready!

### Troubleshooting Initialization

**If database doesn't initialize:**

1. **Check logs:**
   - Go to PostgreSQL service → "Logs"
   - Look for SQL errors

2. **Verify file path:**
   - Ensure `init_fuel_management.sql` is in `backend/db/`
   - Check Dockerfile copies it correctly

3. **Check file permissions:**
   - SQL file should be readable
   - No special characters in path

4. **Manual initialization:**
   - Connect to database: `railway connect postgres` (if service reference works)
   - Or use Railway's Query tab
   - Run SQL manually

## Connection String Formats

### Using Service Reference (Recommended)

```bash
DATABASE_URL=${{postgres.DATABASE_URL}}
```

Railway automatically generates this with correct connection details.

### Using Individual Variables

```bash
DB_HOST=${{postgres.PGHOST}}
DB_PORT=${{postgres.PGPORT}}
DB_NAME=${{postgres.PGDATABASE}}
DB_USER=${{postgres.PGUSER}}
DB_PASSWORD=${{postgres.PGPASSWORD}}
```

### Manual Connection String

If service references don't work:

```bash
DATABASE_URL=postgresql://postgres:your-password@postgres.railway.internal:5432/customersupport
```

**Note**: Railway uses `.railway.internal` for internal service communication.

## Network Configuration

Railway services in the same project can communicate via:
- **Service references**: `${{service.VARIABLE}}` (automatic)
- **Internal DNS**: `service-name.railway.internal` (if references don't work)
- **Environment variables**: Set manually

## Complete Setup Example

### PostgreSQL Service Configuration

**Settings:**
- Name: `postgres`
- Root Directory: `backend/db`
- Dockerfile: `Dockerfile.postgres`

**Environment Variables:**
```
POSTGRES_DB=customersupport
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-generated-password
```

### Backend Service Configuration

**Settings:**
- Name: `backend`
- Root Directory: `backend`
- Dockerfile: `Dockerfile`

**Environment Variables:**
```
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key
DATABASE_URL=${{postgres.DATABASE_URL}}
```

## Verification Checklist

- [ ] PostgreSQL service deployed and running
- [ ] PostgreSQL logs show initialization script ran
- [ ] Backend service deployed
- [ ] `DATABASE_URL` set using service reference
- [ ] Backend logs show "Database connection initialized"
- [ ] Health endpoint returns `"database": true`
- [ ] Can query database successfully

## Advantages of Docker Container vs Managed Service

✅ **Full Control**: You control PostgreSQL version and configuration
✅ **Custom Initialization**: Auto-initialize with your exact schema
✅ **Cost**: May be cheaper depending on usage
✅ **Flexibility**: Can customize PostgreSQL settings

❌ **Maintenance**: You're responsible for backups, updates
❌ **Setup**: More configuration required
❌ **Scaling**: Manual scaling vs automatic

## Backup Strategy

Since you're managing the database:

1. **Regular Backups:**
   ```bash
   # Connect and backup
   railway connect postgres
   pg_dump > backup.sql
   ```

2. **Automated Backups:**
   - Use Railway's cron jobs (if available)
   - Or external backup service
   - Or GitHub Actions for scheduled backups

## Troubleshooting

### Service Reference Not Working

**Problem**: `${{postgres.DATABASE_URL}}` shows as literal string

**Solutions:**
1. ✅ Verify service name matches exactly (case-sensitive)
2. ✅ Use Railway's "Reference" button to auto-generate
3. ✅ Check both services are in the same project
4. ✅ Try manual connection string as fallback

### Database Not Initializing

**Problem**: Tables don't exist after deployment

**Solutions:**
1. ✅ Check PostgreSQL logs for SQL errors
2. ✅ Verify `init_fuel_management.sql` is in correct location
3. ✅ Check Dockerfile copies file correctly
4. ✅ Initialize manually via Railway Query tab

### Connection Errors

**Problem**: Backend can't connect to PostgreSQL

**Solutions:**
1. ✅ Verify `DATABASE_URL` is set correctly
2. ✅ Check PostgreSQL service is running
3. ✅ Verify service name in reference matches
4. ✅ Check network connectivity between services

## Next Steps

1. Create `backend/db/Dockerfile.postgres`
2. Deploy PostgreSQL service on Railway
3. Deploy backend service
4. Connect using service references
5. Verify initialization and connection

Your database will be auto-initialized and ready to use! 🚀

