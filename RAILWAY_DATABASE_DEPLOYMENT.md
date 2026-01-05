# Railway Deployment with Managed PostgreSQL Database

This guide shows you how to deploy your Total Energies Fuel Management AI system on Railway using Railway's managed PostgreSQL database service.

## 🎯 Overview

Railway provides a managed PostgreSQL database service that handles:
- Automatic backups
- High availability
- Easy connection via service references
- Built-in database management tools

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code pushed to GitHub
3. **API Keys**:
   - OpenAI API key (required)
   - Pinecone API key (optional, for RAG features)
4. **Mac Setup** (optional, for local CLI tools):
   - Homebrew (for installing Railway CLI and psql): `brew install node` and `brew install postgresql@15`
   - Or use Railway web interface (no local tools needed)

## 🚀 Step-by-Step Deployment

### Step 1: Create Railway Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository (`customer-support`)
5. Railway will create a new project

### Step 2: Add PostgreSQL Database Service

1. In your Railway project dashboard, click **"+ New"** button
2. Select **"Database"** from the dropdown
3. Choose **"Add PostgreSQL"**
4. Railway will automatically:
   - Create a PostgreSQL 15 instance
   - Generate secure credentials
   - Provide connection details

**✅ You now have a managed PostgreSQL database!**

### Step 3: Deploy Backend Service

1. In the same Railway project, click **"+ New"** again
2. Select **"GitHub Repo"**
3. Choose your repository
4. Railway will try to auto-detect your service

**If auto-detection doesn't work, configure manually:**

1. Click on the newly created service
2. Go to **"Settings"** tab
3. Configure:
   - **Root Directory**: `backend`
   - **Dockerfile Path**: `Dockerfile` (or leave empty if using root)
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 4: Connect Backend to Database

Railway makes this super easy with **service references**:

1. Click on your **backend service**
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**

#### Add Required Environment Variables:

**1. Database Connection (Using Railway Service Reference):**
```
Variable Name: DATABASE_URL
Value: ${{Postgres.DATABASE_URL}}
```

**💡 Tip**: Click the "Reference" button next to the variable field, select your PostgreSQL service, and Railway will auto-fill the reference!

**2. OpenAI API Key:**
```
Variable Name: OPENAI_API_KEY
Value: sk-your-actual-openai-api-key-here
```

**3. Secret Key:**
```
Variable Name: SECRET_KEY
Value: [Generate a strong random string - use openssl rand -hex 32]
```

#### Optional Environment Variables:

```
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=customer-support
MODEL_NAME=gpt-4
TEMPERATURE=0.7
LOG_LEVEL=INFO
```

**4. CORS Origins** (add after you deploy frontend):
```
Variable Name: CORS_ORIGINS
Value: ["https://your-frontend-service.railway.app"]
```

### Step 5: Initialize Database Schema

Now you need to populate your Railway PostgreSQL database with the schema and sample data.

#### Option A: Using Railway Web Interface (Easiest)

1. Go to your **PostgreSQL service** in Railway dashboard
2. Click on the **"Data"** tab
3. Click **"Query"** button (or "Connect" → "Query")
4. This opens Railway's built-in SQL editor
5. Open `backend/db/init_fuel_management.sql` from your local repository
6. Copy the **entire contents** of the file
7. Paste into Railway's SQL editor
8. Click **"Run"** or press `Ctrl+Enter` (Windows) / `Cmd+Enter` (Mac)
9. Wait for execution to complete (may take 30-60 seconds)

**✅ Database is now initialized!**

#### Option B: Using Railway CLI (Mac)

**Install Railway CLI on Mac:**

```bash
# Install Node.js first (if not installed)
brew install node

# Install Railway CLI
npm i -g @railway/cli
```

**Then:**

1. **Login to Railway:**
   ```bash
   railway login
   ```
   This will open your browser for authentication.

2. **Navigate to your project directory:**
   ```bash
   cd /Users/danialamin/Documents/GitHub/customer-support
   ```

3. **Link to your project:**
   ```bash
   railway link
   ```
   (Select your project when prompted)

4. **Connect to PostgreSQL:**
   ```bash
   railway connect postgres
   ```
   This opens a psql session connected to your Railway database.

5. **Run initialization script:**
   ```sql
   \i backend/db/init_fuel_management.sql
   ```
   
   **OR** if the file isn't accessible, copy-paste the SQL directly:
   ```sql
   -- Paste the entire contents of init_fuel_management.sql here
   ```

6. **Verify tables were created:**
   ```sql
   \dt
   ```
   You should see tables like `fuel_stations`, `vehicles`, `fuel_transactions`, etc.

7. **Exit psql:**
   ```sql
   \q
   ```
   Or press `Ctrl+D` (Mac Terminal)

#### Option C: Using psql from Local Machine (Mac)

**First, install PostgreSQL client on Mac (if not already installed):**

```bash
# Using Homebrew (recommended)
brew install postgresql@15

# Or install full PostgreSQL
brew install postgresql
```

**Then:**

1. **Get connection string from Railway:**
   - Go to PostgreSQL service → **"Variables"** tab
   - Copy the `DATABASE_URL` value
   - Or use Railway CLI: `railway variables`

2. **Navigate to your project directory:**
   ```bash
   cd /Users/danialamin/Documents/GitHub/customer-support
   ```

3. **Run initialization:**
   ```bash
   # Railway PostgreSQL requires SSL - add sslmode parameter
   psql "$DATABASE_URL?sslmode=require" -f backend/db/init_fuel_management.sql
   ```
   
   **If you get SSL errors, see [RAILWAY_PSQL_SSL_FIX.md](./RAILWAY_PSQL_SSL_FIX.md) for troubleshooting.**
   
   **If you get SSL errors, try:**
   ```bash
   # Option 1: Require SSL (recommended)
   psql "$DATABASE_URL?sslmode=require" -f backend/db/init_fuel_management.sql
   
   # Option 2: Prefer SSL (fallback)
   psql "$DATABASE_URL?sslmode=prefer" -f backend/db/init_fuel_management.sql
   
   # Option 3: Use environment variable with SSL
   export PGDATABASE=$(echo $DATABASE_URL | sed 's/.*\/\([^?]*\).*/\1/')
   psql "$DATABASE_URL?sslmode=require" -f backend/db/init_fuel_management.sql
   ```

**💡 Mac Tip**: If `psql` command is not found, you may need to add it to your PATH:
```bash
# For Homebrew PostgreSQL
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Step 6: Verify Database Connection

1. Go to your **backend service** in Railway
2. Click on **"Deployments"** tab
3. Check the latest deployment logs
4. Look for messages like:
   - `"Database configured: True"`
   - `"Starting up application..."`
   - No database connection errors

### Step 7: Generate Public URL for Backend

1. Click on your **backend service**
2. Go to **"Settings"** tab
3. Scroll to **"Networking"** section
4. Click **"Generate Domain"**
5. Railway will create a public URL like: `https://your-backend-production.up.railway.app`
6. **Copy this URL** - you'll need it for the frontend

### Step 8: Test Backend API

1. Open your backend URL in a browser: `https://your-backend.railway.app/api/v1/health`
2. You should see:
   ```json
   {
     "status": "healthy",
     "services": {
       "pinecone": true/false,
       "database": true
     }
   }
   ```
3. If `"database": true`, your connection is working! ✅

### Step 9: Deploy Frontend (Optional)

1. In Railway project, click **"+ New"** → **"GitHub Repo"**
2. Select your repository again
3. Configure:
   - **Root Directory**: `frontend`
   - **Dockerfile Path**: `Dockerfile`

4. **Add Environment Variable (CRITICAL):**
   ```
   Variable Name: VITE_API_URL
   Value: https://your-backend-production.up.railway.app
   ```
   **⚠️ IMPORTANT**: 
   - Use the **backend URL** from Step 7, NOT the frontend URL!
   - Set this variable BEFORE building/deploying
   - Railway will automatically pass it to the build process
   
   **Example:**
   - Backend URL: `https://backend-production-abc123.up.railway.app`
   - Frontend URL: `https://frontend-production-xyz789.up.railway.app`
   - Set `VITE_API_URL` to: `https://backend-production-abc123.up.railway.app`
   
   **Why?** The frontend needs to know where the backend API is. Without this, API calls will fail!
   
   **⚠️ After setting the variable:**
   - Railway will automatically trigger a rebuild
   - Wait for the build to complete
   - The new build will have the correct API URL embedded

5. **Generate Domain** for frontend (same as Step 7)

6. **Update Backend CORS:**
   - Go to backend service → **"Variables"**
   - Update `CORS_ORIGINS`:
     ```
     ["https://your-frontend-production.up.railway.app"]
     ```
   - Redeploy backend (Railway auto-redeploys on variable change)

## 🔍 Verifying Database Connection

### Check Database Tables

1. Go to PostgreSQL service → **"Data"** tab → **"Query"**
2. Run:
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public';
   ```
3. You should see tables like:
   - `fuel_types`
   - `fuel_stations`
   - `vehicles`
   - `fuel_cards`
   - `fuel_transactions`
   - `fuel_refills`
   - `fuel_consumption_reports`
   - `fuel_support_tickets`

### Check Sample Data

```sql
SELECT COUNT(*) FROM fuel_stations;
-- Should return: 10

SELECT COUNT(*) FROM vehicles;
-- Should return: 15

SELECT COUNT(*) FROM fuel_transactions;
-- Should return: 50
```

## 🎯 Railway Service References Explained

Railway's service references (`${{ServiceName.VARIABLE}}`) automatically:
- ✅ Connect services together
- ✅ Update when credentials change
- ✅ Keep connections secure
- ✅ Work across service restarts

**Common PostgreSQL References:**
- `${{Postgres.DATABASE_URL}}` - Full connection string (recommended)
- `${{Postgres.PGHOST}}` - Database host
- `${{Postgres.PGPORT}}` - Database port
- `${{Postgres.PGDATABASE}}` - Database name
- `${{Postgres.PGUSER}}` - Database user
- `${{Postgres.PGPASSWORD}}` - Database password

**💡 Best Practice**: Use `${{Postgres.DATABASE_URL}}` - it includes everything!

## 🔧 Troubleshooting

### Database Connection Fails

**Problem**: Backend can't connect to database

**Solutions**:
1. ✅ Verify `DATABASE_URL` uses `${{Postgres.DATABASE_URL}}`
2. ✅ Check PostgreSQL service is running (green status)
3. ✅ Check backend logs for connection errors
4. ✅ Ensure database is initialized (see Step 5)

### Database Not Initialized

**Problem**: Tables don't exist

**Solutions**:
1. ✅ Run `init_fuel_management.sql` in Railway's Query tab
2. ✅ Check for SQL errors in the query results
3. ✅ Verify you're connected to the correct database

### Service Reference Not Working

**Problem**: `${{Postgres.DATABASE_URL}}` shows as literal string

**Solutions**:
1. ✅ Ensure PostgreSQL service is named "Postgres" (or match the name)
2. ✅ Use Railway's "Reference" button to auto-generate
3. ✅ Check both services are in the same project

### Backend Won't Start

**Problem**: Deployment fails

**Solutions**:
1. ✅ Check all required environment variables are set
2. ✅ Verify `DATABASE_URL` is correct
3. ✅ Check deployment logs for specific errors
4. ✅ Ensure Dockerfile is correct

### Frontend Can't Connect to Backend API

**Problem**: Frontend shows API errors or can't reach backend, or still uses frontend URL

**Common Issues:**

1. **VITE_API_URL not set before build:**
   - Vite environment variables are embedded at BUILD TIME, not runtime
   - If you set `VITE_API_URL` after the build, it won't work
   - **Solution**: Set `VITE_API_URL` BEFORE deploying, or trigger a rebuild after setting it

2. **Setting VITE_API_URL to frontend URL instead of backend URL:**
   - ❌ `VITE_API_URL` = `https://frontend-production-xyz789.up.railway.app` (WRONG!)
   - ✅ `VITE_API_URL` = `https://backend-production-abc123.up.railway.app` (CORRECT!)

**Example of Wrong Setup:**
- Backend URL: `https://backend-production-abc123.up.railway.app`
- Frontend URL: `https://frontend-production-xyz789.up.railway.app`
- ❌ `VITE_API_URL` = `https://frontend-production-xyz789.up.railway.app` (WRONG!)

**Correct Setup:**
- ✅ `VITE_API_URL` = `https://backend-production-abc123.up.railway.app` (CORRECT!)

**Solutions**:
1. ✅ Go to frontend service → **"Variables"** tab
2. ✅ Verify `VITE_API_URL` is set to your **backend URL** (not frontend URL)
3. ✅ **CRITICAL**: After setting/changing `VITE_API_URL`, Railway should auto-rebuild
   - If not, manually trigger a redeploy: Service → "Deployments" → "Redeploy"
   - Wait for build to complete (check build logs)
4. ✅ Verify the build picked up the variable:
   - Check build logs for any errors
   - After deployment, open browser console (F12)
   - Look for the debug log: `🔧 API Configuration:` 
   - Verify `API_BASE_URL` shows your backend URL
5. ✅ Check browser console (F12) for API errors
6. ✅ Verify backend service is running and accessible
7. ✅ Test backend directly: `https://your-backend.railway.app/api/v1/health`
8. ✅ Verify CORS is configured correctly in backend (`CORS_ORIGINS` includes frontend URL)

**How to verify VITE_API_URL is working:**
1. Open your deployed frontend in browser
2. Open Developer Tools (F12) → Console tab
3. Look for: `🔧 API Configuration: { VITE_API_URL: '...', API_BASE_URL: '...' }`
4. Verify `API_BASE_URL` matches your backend URL

## 📊 Database Management

### View Database in Railway

1. Go to PostgreSQL service
2. Click **"Data"** tab
3. Use **"Query"** for SQL queries
4. Use **"Connect"** for psql terminal

### Backup Database

Railway automatically backs up your database, but you can also:

1. Use Railway CLI (Mac):
   ```bash
   railway connect postgres
   pg_dump > backup.sql
   # Exit with Ctrl+D or \q
   ```
   
   **Mac Note**: The backup file will be saved in your current directory. You can specify a path:
   ```bash
   pg_dump > ~/Downloads/backup_$(date +%Y%m%d).sql
   ```

2. Or use Railway's built-in backup feature (if available in your plan)

### Monitor Database

- **Metrics**: PostgreSQL service → "Metrics" tab
- **Logs**: PostgreSQL service → "Logs" tab
- **Usage**: Check database size and connection count

## ✅ Deployment Checklist

- [ ] Railway project created
- [ ] PostgreSQL database service added
- [ ] Backend service deployed
- [ ] `DATABASE_URL` set to `${{Postgres.DATABASE_URL}}`
- [ ] `OPENAI_API_KEY` configured
- [ ] `SECRET_KEY` set (strong random string)
- [ ] Database initialized with `init_fuel_management.sql`
- [ ] Database tables verified
- [ ] Backend health check passes (`/api/v1/health`)
- [ ] Backend public URL generated
- [ ] Frontend deployed (optional)
- [ ] Frontend `VITE_API_URL` set to backend URL
- [ ] CORS configured for frontend URL
- [ ] All services running and healthy

## 🎉 You're Done!

Your Total Energies Fuel Management AI system is now running on Railway with a managed PostgreSQL database!

**Next Steps:**
- Test your API endpoints
- Monitor usage in Railway dashboard
- Set up custom domains (optional)
- Configure backups (if needed)

## 🍎 Mac Users

If you're on a Mac, see [MAC_SETUP.md](./MAC_SETUP.md) for:
- Homebrew installation
- Mac-specific terminal commands
- Keyboard shortcuts
- Troubleshooting Mac-specific issues

## 📚 Additional Resources

- [Railway PostgreSQL Docs](https://docs.railway.app/databases/postgresql)
- [Railway Service References](https://docs.railway.app/develop/variables#service-reference-variables)
- [Railway CLI Docs](https://docs.railway.app/develop/cli)
- [Mac Setup Guide](./MAC_SETUP.md) - Mac-specific setup instructions

