# Running Your Own Database Service

This guide shows you how to use your own PostgreSQL database instead of Railway's managed service.

## Options for Your Own Database

### Option 1: Docker Compose PostgreSQL (Already Set Up!) ✅

You already have PostgreSQL configured in `docker-compose.yml`. Just use it!

**To use the Docker Compose database:**

1. **Start the database:**
   ```bash
   docker-compose up -d postgres
   ```

2. **Set environment variables** (in `.env` or Railway):
   ```bash
   # Option A: Use DATABASE_URL
   DATABASE_URL=postgresql://postgres:postgres@postgres:5432/customersupport
   
   # Option B: Use individual variables (for Docker Compose)
   DB_HOST=postgres
   DB_PORT=5432
   DB_NAME=customersupport
   DB_USER=postgres
   DB_PASSWORD=postgres
   ```

3. **The database is automatically initialized** with `init_fuel_management.sql` when the container starts!

**For Railway deployment with Docker Compose database:**
- The database runs in the same Docker network
- Use service name `postgres` as the host
- No SSL required (internal network)

### Option 2: Local PostgreSQL on Mac

**Install PostgreSQL:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Create database:**
```bash
# Create database and user
createdb customersupport
createuser -s postgres  # Or create a specific user

# Initialize schema
psql customersupport -f backend/db/init_fuel_management.sql
```

**Configure connection:**
```bash
# In .env or Railway variables
DATABASE_URL=postgresql://postgres@localhost:5432/customersupport

# Or use individual variables
DB_HOST=localhost
DB_PORT=5432
DB_NAME=customersupport
DB_USER=postgres
DB_PASSWORD=  # Leave empty if no password
```

### Option 3: Cloud Database Services

#### AWS RDS PostgreSQL

1. **Create RDS PostgreSQL instance** in AWS Console
2. **Get connection details:**
   - Endpoint: `your-db.xxxxx.us-east-1.rds.amazonaws.com`
   - Port: `5432`
   - Database name, username, password

3. **Configure:**
   ```bash
   DATABASE_URL=postgresql://username:password@your-db.xxxxx.us-east-1.rds.amazonaws.com:5432/dbname?sslmode=require
   ```

#### Google Cloud SQL

1. **Create Cloud SQL PostgreSQL instance**
2. **Get connection details** from GCP Console
3. **Configure:**
   ```bash
   DATABASE_URL=postgresql://username:password@/dbname?host=/cloudsql/project:region:instance
   ```

#### DigitalOcean Managed Database

1. **Create PostgreSQL database** in DigitalOcean
2. **Get connection string** from dashboard
3. **Configure:**
   ```bash
   DATABASE_URL=postgresql://username:password@host:port/dbname?sslmode=require
   ```

#### Supabase (Free Tier Available)

1. **Create project** at [supabase.com](https://supabase.com)
2. **Get connection string** from project settings
3. **Configure:**
   ```bash
   DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres?sslmode=require
   ```

### Option 4: Self-Hosted PostgreSQL Server

If you have your own server/VPS:

1. **Install PostgreSQL:**
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # On CentOS/RHEL
   sudo yum install postgresql-server postgresql-contrib
   ```

2. **Configure PostgreSQL:**
   ```bash
   # Edit postgresql.conf
   sudo nano /etc/postgresql/15/main/postgresql.conf
   # Set: listen_addresses = '*'
   
   # Edit pg_hba.conf for remote access
   sudo nano /etc/postgresql/15/main/pg_hba.conf
   # Add: host all all 0.0.0.0/0 md5
   
   # Restart PostgreSQL
   sudo systemctl restart postgresql
   ```

3. **Create database:**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE customersupport;
   CREATE USER youruser WITH PASSWORD 'yourpassword';
   GRANT ALL PRIVILEGES ON DATABASE customersupport TO youruser;
   \q
   ```

4. **Initialize schema:**
   ```bash
   psql -h your-server-ip -U youruser -d customersupport -f backend/db/init_fuel_management.sql
   ```

5. **Configure connection:**
   ```bash
   DATABASE_URL=postgresql://youruser:yourpassword@your-server-ip:5432/customersupport
   ```

## Configuration Methods

### Method 1: DATABASE_URL (Recommended)

Single connection string with all details:

```bash
DATABASE_URL=postgresql://username:password@host:port/database
```

**Examples:**
- Local: `postgresql://postgres@localhost:5432/customersupport`
- Docker: `postgresql://postgres:postgres@postgres:5432/customersupport`
- Cloud (SSL): `postgresql://user:pass@host:5432/db?sslmode=require`

### Method 2: Individual Variables

Separate variables for each component:

```bash
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=customersupport
DB_USER=your-username
DB_PASSWORD=your-password
```

The application will automatically construct the connection string from these.

## SSL Configuration

### When SSL is Required

Most cloud databases require SSL:
- Railway PostgreSQL ✅
- AWS RDS ✅
- Google Cloud SQL ✅
- DigitalOcean ✅
- Supabase ✅

### When SSL is NOT Required

- Local PostgreSQL (localhost)
- Docker Compose (internal network)
- Self-hosted on same network

### SSL Connection String Format

```bash
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

**SSL Modes:**
- `sslmode=require` - Requires SSL (most cloud services)
- `sslmode=prefer` - Prefers SSL, falls back if not available
- `sslmode=disable` - No SSL (local/Docker only)

## Deployment Scenarios

### Scenario 1: Railway Backend + Docker Compose Database

If you want to run the database in Docker Compose but deploy backend to Railway:

**Not recommended** - Docker Compose database is only accessible locally. Instead:
- Use Railway's managed PostgreSQL, OR
- Use a cloud database service

### Scenario 2: Railway Backend + Cloud Database

**Best for production:**

1. **Set up cloud database** (AWS RDS, Supabase, etc.)
2. **Get connection string**
3. **Set in Railway backend service:**
   ```
   DATABASE_URL=postgresql://user:pass@cloud-host:5432/db?sslmode=require
   ```

### Scenario 3: Local Development + Local Database

**Best for development:**

1. **Use Docker Compose:**
   ```bash
   docker-compose up -d postgres
   ```

2. **Set in `.env`:**
   ```bash
   DB_HOST=postgres
   DB_PORT=5432
   DB_NAME=customersupport
   DB_USER=postgres
   DB_PASSWORD=postgres
   ```

3. **Or use local PostgreSQL:**
   ```bash
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=customersupport
   DB_USER=postgres
   DB_PASSWORD=
   ```

## Initializing Your Database

### Using Docker Compose

The database is **automatically initialized** when the container starts:
- Schema file: `backend/db/init_fuel_management.sql`
- Mounted at: `/docker-entrypoint-initdb.d/init_fuel_management.sql`
- Runs automatically on first container start

### Manual Initialization

For other database services:

```bash
# Using psql
psql "$DATABASE_URL" -f backend/db/init_fuel_management.sql

# With SSL (for cloud databases)
psql "$DATABASE_URL?sslmode=require" -f backend/db/init_fuel_management.sql

# Using individual variables
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f backend/db/init_fuel_management.sql
```

## Migration from Railway Database

If you want to migrate data from Railway to your own database:

### Step 1: Export from Railway

```bash
# Connect to Railway database
railway connect postgres

# Export data
pg_dump "$DATABASE_URL?sslmode=require" > backup.sql
```

### Step 2: Import to Your Database

```bash
# Import to your database
psql "$YOUR_DATABASE_URL" < backup.sql

# Or with SSL
psql "$YOUR_DATABASE_URL?sslmode=require" < backup.sql
```

## Testing Your Connection

### Test from Terminal

```bash
# Test connection
psql "$DATABASE_URL" -c "SELECT version();"

# With SSL
psql "$DATABASE_URL?sslmode=require" -c "SELECT version();"

# Test with individual variables
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT version();"
```

### Test from Application

1. **Start your backend:**
   ```bash
   docker-compose up backend
   ```

2. **Check health endpoint:**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

3. **Look for:**
   ```json
   {
     "status": "healthy",
     "services": {
       "database": true
     }
   }
   ```

## Security Best Practices

### For Production Databases

1. **Use strong passwords:**
   ```bash
   # Generate strong password
   openssl rand -base64 32
   ```

2. **Restrict network access:**
   - Use firewall rules
   - Whitelist only your application IPs
   - Use VPC/private networks when possible

3. **Enable SSL:**
   ```bash
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   ```

4. **Use connection pooling:**
   - The application uses NullPool (good for serverless)
   - For high-traffic, consider PgBouncer

5. **Regular backups:**
   ```bash
   # Automated backup script
   pg_dump "$DATABASE_URL?sslmode=require" | gzip > backup_$(date +%Y%m%d).sql.gz
   ```

## Troubleshooting

### Connection Refused

**Problem**: Can't connect to database

**Solutions**:
1. ✅ Check database is running
2. ✅ Verify host/port are correct
3. ✅ Check firewall rules
4. ✅ Verify credentials

### SSL Required Error

**Problem**: "SSL connection required"

**Solutions**:
1. ✅ Add `?sslmode=require` to connection string
2. ✅ Verify database supports SSL
3. ✅ Check SSL certificates if using `sslmode=verify-full`

### Authentication Failed

**Problem**: "password authentication failed"

**Solutions**:
1. ✅ Verify username/password
2. ✅ Check user has access to database
3. ✅ Verify database name is correct

### Database Not Found

**Problem**: "database does not exist"

**Solutions**:
1. ✅ Create database first
2. ✅ Verify database name in connection string
3. ✅ Check user has permissions

## Quick Reference

### Connection String Formats

```bash
# Local (no SSL)
postgresql://user@localhost:5432/db

# Docker Compose (no SSL)
postgresql://user:pass@postgres:5432/db

# Cloud (SSL required)
postgresql://user:pass@host:5432/db?sslmode=require

# With custom port
postgresql://user:pass@host:5433/db?sslmode=require
```

### Environment Variables

```bash
# Method 1: DATABASE_URL
DATABASE_URL=postgresql://user:pass@host:5432/db

# Method 2: Individual variables
DB_HOST=host
DB_PORT=5432
DB_NAME=db
DB_USER=user
DB_PASSWORD=pass
```

## Recommended Setup by Use Case

### Development
- **Docker Compose PostgreSQL** ✅
- No SSL needed
- Auto-initialized
- Easy to reset

### Production (Small/Medium)
- **Supabase** (free tier) or **Railway PostgreSQL**
- Managed service
- Automatic backups
- SSL included

### Production (Large Scale)
- **AWS RDS** or **Google Cloud SQL**
- High availability
- Automated backups
- Monitoring included

### Self-Hosted
- **Your own VPS/server**
- Full control
- Requires maintenance
- Good for compliance

## Next Steps

1. **Choose your database option** from above
2. **Set up the database** following the instructions
3. **Configure connection** in your `.env` or Railway variables
4. **Initialize schema** using `init_fuel_management.sql`
5. **Test connection** using the health endpoint
6. **Deploy and verify** everything works

Need help? Check the troubleshooting section or see the main deployment guides.

