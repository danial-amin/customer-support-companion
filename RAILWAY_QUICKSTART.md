# Railway Quick Start Guide

## 🚀 Quick Deployment (5 minutes)

### 1. Connect Repository to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository

### 2. Add Railway PostgreSQL Database Service

1. In Railway dashboard → Click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway automatically creates a managed PostgreSQL database
4. ✅ Your database is ready!

### 3. Deploy Backend

1. Click **"+ New"** → **"GitHub Repo"** → Select your repository
2. Railway auto-detects your `backend/Dockerfile`
3. If not detected, configure:
   - **Root Directory**: `backend`
   - **Dockerfile**: `Dockerfile`

### 4. Connect Backend to Database

In your backend service → **"Variables"** tab, add:

```bash
# Required - Use Railway's service reference!
DATABASE_URL=${{Postgres.DATABASE_URL}}

OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=your-random-secret-key-here

# Optional
PINECONE_API_KEY=your-pinecone-key
CORS_ORIGINS=["https://your-frontend.railway.app"]
```

**💡 Tip**: Click "Reference" button and select your PostgreSQL service to auto-fill `${{Postgres.DATABASE_URL}}`

### 5. Initialize Database

**Easiest Method: Railway Web Interface**
1. Go to **PostgreSQL service** → **"Data"** tab
2. Click **"Query"** button
3. Open `backend/db/init_fuel_management.sql` locally
4. Copy entire file contents
5. Paste into Railway's SQL editor
6. Click **"Run"** (or `Cmd+Enter` / `Ctrl+Enter`)
7. ✅ Database initialized!

**Alternative: Railway CLI**
```bash
railway login
railway link
railway connect postgres
# Then paste SQL from init_fuel_management.sql
```

### 6. Generate Public URL

1. Backend service → **"Settings"** → **"Generate Domain"**
2. Copy the URL (e.g., `https://backend-production.up.railway.app`)

### 7. Deploy Frontend (Optional)

1. **"+ New"** → **"GitHub Repo"** → Select repository
2. Configure:
   - **Root Directory**: `frontend`
   - **Dockerfile**: `Dockerfile`
3. **Add Environment Variable (CRITICAL):**
   ```
   Variable Name: VITE_API_URL
   Value: https://your-backend-url.railway.app
   ```
   **⚠️ IMPORTANT**: This must be your **backend URL**, not the frontend URL!
   
   Example:
   - If backend is: `https://backend-production-abc.up.railway.app`
   - Set `VITE_API_URL` to: `https://backend-production-abc.up.railway.app`
4. Generate domain for frontend

## ✅ Verify Deployment

1. Visit your backend URL: `https://your-backend.railway.app/api/v1/health`
2. Should return: `{"status": "healthy", ...}`

## 🔧 Common Issues

**Backend won't start?**
- Check all environment variables are set
- Verify `DATABASE_URL` is correct
- Check logs in Railway dashboard

**Database connection errors?**
- Ensure PostgreSQL service is running
- Verify `DATABASE_URL` uses `${{Postgres.DATABASE_URL}}`
- Check database is initialized

**CORS errors?**
- Update `CORS_ORIGINS` to include your frontend URL
- Format: `["https://your-frontend.railway.app"]`

## 📚 Full Documentation

- **Using Railway Database Service**: See [RAILWAY_DATABASE_DEPLOYMENT.md](./RAILWAY_DATABASE_DEPLOYMENT.md) for detailed guide
- **General Deployment**: See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for alternative methods

## 🆘 Need Help?

- Check Railway logs in dashboard
- Review [Railway Docs](https://docs.railway.app)
- Join [Railway Discord](https://discord.gg/railway)

