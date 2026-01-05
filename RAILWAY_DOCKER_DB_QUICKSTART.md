# Quick Start: PostgreSQL Docker Container on Railway

Deploy your own PostgreSQL container on Railway that auto-initializes with your schema.

## 🚀 5-Minute Setup

### 1. Deploy PostgreSQL Container

1. Railway Dashboard → **"+ New"** → **"GitHub Repo"**
2. Select your repository
3. **Settings:**
   - **Name**: `postgres`
   - **Root Directory**: `backend/db`
   - **Dockerfile Path**: `Dockerfile.postgres`
4. **Environment Variables:**
   ```
   POSTGRES_DB=customersupport
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your-strong-password
   ```
5. Railway will build and deploy - database auto-initializes! ✅

### 2. Deploy Backend

1. **"+ New"** → **"GitHub Repo"** → Select repository
2. **Settings:**
   - **Root Directory**: `backend`
   - **Dockerfile Path**: `Dockerfile`
3. **Environment Variables:**
   ```
   OPENAI_API_KEY=your-key
   SECRET_KEY=your-secret
   DATABASE_URL=${{postgres.DATABASE_URL}}
   ```

### 3. Verify

1. Check PostgreSQL logs → Should see initialization
2. Check backend logs → Should see "Database connection initialized"
3. Test: `curl https://your-backend.railway.app/api/v1/health`

## ✅ Done!

Your PostgreSQL container is running and auto-initialized with your schema!

**Full guide:** [RAILWAY_DOCKER_DATABASE.md](./RAILWAY_DOCKER_DATABASE.md)

