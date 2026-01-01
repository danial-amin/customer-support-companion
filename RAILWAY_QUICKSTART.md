# Railway Quick Start Guide

## 🚀 Quick Deployment (5 minutes)

### 1. Connect Repository to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository

### 2. Add PostgreSQL Database

1. In Railway dashboard → "New Service"
2. Select "Database" → "Add PostgreSQL"
3. Railway will create the database automatically

### 3. Deploy Backend

1. Railway auto-detects your `backend/Dockerfile`
2. If not detected, configure:
   - **Root Directory**: `backend`
   - **Dockerfile**: `Dockerfile`

### 4. Set Environment Variables

In your backend service, add:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Optional
PINECONE_API_KEY=your-pinecone-key
CORS_ORIGINS=["https://your-frontend.railway.app"]
```

**Note**: `${{Postgres.DATABASE_URL}}` automatically connects to your PostgreSQL service.

### 5. Initialize Database

**Option A: Using Railway Web Terminal**
1. Go to PostgreSQL service → "Data" tab
2. Click "Query"
3. Copy/paste contents of `backend/db/init_fuel_management.sql`
4. Execute

**Option B: Using Railway CLI**
```bash
railway login
railway link
railway connect postgres
# Then paste: \i backend/db/init_fuel_management.sql
```

### 6. Generate Public URL

1. Backend service → "Settings" → "Generate Domain"
2. Copy the URL (e.g., `https://backend-production.up.railway.app`)

### 7. Deploy Frontend (Optional)

1. "New Service" → "GitHub Repo"
2. Configure:
   - **Root Directory**: `frontend`
   - **Dockerfile**: `Dockerfile`
3. Add environment variable:
   ```
   VITE_API_URL=https://your-backend-url.railway.app
   ```
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

See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for detailed instructions.

## 🆘 Need Help?

- Check Railway logs in dashboard
- Review [Railway Docs](https://docs.railway.app)
- Join [Railway Discord](https://discord.gg/railway)

