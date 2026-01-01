# Railway Deployment Guide

This guide will help you deploy the Total Energies Fuel Management AI system to Railway.

## Prerequisites

1. A [Railway](https://railway.app) account
2. A GitHub account (for connecting your repository)
3. API keys for:
   - OpenAI (required)
   - Pinecone (optional, for RAG features)
4. Railway CLI (optional, for local testing)

## Deployment Options

Railway supports two deployment approaches:

### Option 1: Multi-Service Deployment (Recommended)

Deploy backend, frontend, and database as separate Railway services.

### Option 2: Single Service Deployment

Deploy only the backend, and optionally use Railway's PostgreSQL service.

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. Push your code to GitHub (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

### Step 2: Create Railway Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect your project

### Step 3: Deploy Backend Service

1. In Railway dashboard, click "New Service"
2. Select "GitHub Repo" and choose your repository
3. Railway will auto-detect the Dockerfile in `backend/Dockerfile`
4. If not detected, configure:
   - **Root Directory**: `backend`
   - **Dockerfile Path**: `Dockerfile`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 4: Add PostgreSQL Database

1. In Railway dashboard, click "New Service"
2. Select "Database" → "Add PostgreSQL"
3. Railway will create a PostgreSQL instance
4. Note the connection details (you'll need them for environment variables)

### Step 5: Configure Environment Variables

In your backend service, add these environment variables:

#### Required Variables:
```
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here_use_a_strong_random_string
```

#### Database Variables (from Railway PostgreSQL service):
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
# OR manually set:
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
DB_NAME=${{Postgres.PGDATABASE}}
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
```

#### Optional Variables:
```
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=customer-support
CORS_ORIGINS=["https://your-frontend-domain.railway.app"]
MODEL_NAME=gpt-4
TEMPERATURE=0.7
LOG_LEVEL=INFO
```

**Note**: Railway provides service references like `${{Postgres.DATABASE_URL}}` that automatically connect services.

### Step 6: Initialize Database

After the PostgreSQL service is running, you need to initialize it with your schema:

1. Get your database connection string from Railway PostgreSQL service
2. Use Railway's built-in PostgreSQL terminal or connect via CLI:
   ```bash
   railway connect postgres
   ```
3. Run the initialization script:
   ```sql
   \i backend/db/init_fuel_management.sql
   ```
   Or via psql:
   ```bash
   psql $DATABASE_URL -f backend/db/init_fuel_management.sql
   ```

Alternatively, you can use Railway's "Deploy Script" feature to run migrations automatically.

### Step 7: Deploy Frontend Service (Optional)

1. In Railway dashboard, click "New Service"
2. Select "GitHub Repo" and choose your repository
3. Configure:
   - **Root Directory**: `frontend`
   - **Dockerfile Path**: `Dockerfile`
   - **Build Command**: `npm ci && npm run build`
4. Add environment variable:
   ```
   VITE_API_URL=https://your-backend-service.railway.app
   ```

### Step 8: Configure CORS

Update your backend service's `CORS_ORIGINS` environment variable to include your frontend URL:

```
CORS_ORIGINS=["https://your-frontend-service.railway.app","http://localhost:3000"]
```

### Step 9: Generate Public URLs

1. In each service, go to "Settings"
2. Click "Generate Domain" to get a public URL
3. Note the URLs for:
   - Backend service (e.g., `https://backend-production.up.railway.app`)
   - Frontend service (e.g., `https://frontend-production.up.railway.app`)

### Step 10: Update Frontend API URL

If deploying frontend separately, update the API URL:

1. In frontend service environment variables:
   ```
   VITE_API_URL=https://your-backend-service.railway.app
   ```
2. Rebuild the frontend service

## Environment Variables Reference

### Backend Service

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | ✅ Yes | OpenAI API key | `sk-...` |
| `SECRET_KEY` | ✅ Yes | Secret key for security | Random string |
| `DATABASE_URL` | ✅ Yes | PostgreSQL connection string | `postgresql://...` |
| `PINECONE_API_KEY` | ❌ No | Pinecone API key for RAG | `...` |
| `PINECONE_ENVIRONMENT` | ❌ No | Pinecone environment | `us-east-1` |
| `PINECONE_INDEX_NAME` | ❌ No | Pinecone index name | `customer-support` |
| `CORS_ORIGINS` | ❌ No | Allowed CORS origins (JSON array) | `["https://..."]` |
| `MODEL_NAME` | ❌ No | OpenAI model to use | `gpt-4` |
| `TEMPERATURE` | ❌ No | LLM temperature | `0.7` |
| `LOG_LEVEL` | ❌ No | Logging level | `INFO` |

### Frontend Service

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_API_URL` | ✅ Yes | Backend API URL | `https://backend.railway.app` |
| `VITE_API_KEY` | ❌ No | API key (if using API key auth) | `...` |

## Database Initialization

### Option 1: Using Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Connect to database
railway connect postgres

# Run initialization script
\i backend/db/init_fuel_management.sql
```

### Option 2: Using Railway Web Terminal

1. Go to your PostgreSQL service in Railway
2. Click "Data" tab
3. Click "Query" or "Connect"
4. Copy and paste the contents of `backend/db/init_fuel_management.sql`
5. Execute

### Option 3: Using psql from Local Machine

```bash
# Get connection string from Railway
railway variables

# Connect and run script
psql $DATABASE_URL -f backend/db/init_fuel_management.sql
```

## Troubleshooting

### Backend won't start

1. Check logs in Railway dashboard
2. Verify all required environment variables are set
3. Check that `DATABASE_URL` is correct
4. Ensure port is set to `$PORT` (Railway provides this)

### Database connection errors

1. Verify `DATABASE_URL` is correctly set
2. Check that PostgreSQL service is running
3. Ensure database is initialized with schema

### CORS errors

1. Update `CORS_ORIGINS` to include your frontend URL
2. Ensure URLs are in JSON array format: `["https://..."]`

### Frontend can't connect to backend

1. Verify `VITE_API_URL` is set correctly
2. Check backend service is running
3. Verify CORS is configured correctly

### Build failures

1. Check Dockerfile paths are correct
2. Verify all dependencies are in `requirements.txt`
3. Check build logs for specific errors

## Monitoring

Railway provides:
- **Logs**: Real-time logs for each service
- **Metrics**: CPU, memory, and network usage
- **Deployments**: History of all deployments
- **Health Checks**: Automatic health monitoring

## Cost Optimization

1. **Use Railway's free tier** for development
2. **Scale down** services when not in use
3. **Use Railway's sleep feature** for non-production environments
4. **Monitor usage** in Railway dashboard

## Production Checklist

- [ ] All environment variables configured
- [ ] Database initialized with schema
- [ ] CORS configured for production domains
- [ ] API keys secured (not in code)
- [ ] Health checks configured
- [ ] Monitoring set up
- [ ] Backup strategy for database
- [ ] Custom domains configured (optional)
- [ ] SSL certificates active (automatic on Railway)

## Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

## Support

If you encounter issues:
1. Check Railway logs
2. Review this guide
3. Check Railway documentation
4. Ask in Railway Discord community

