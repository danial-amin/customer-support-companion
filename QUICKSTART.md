# Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- Pinecone API key (for RAG functionality)
- PostgreSQL (optional, for SQL agent)

## Setup Steps

### 1. Clone and Navigate

```bash
cd customer-support
```

### 2. Configure Environment

Run the setup script:

```bash
./setup.sh
```

Or manually create a `.env` file in the root directory:

```bash
# Copy the example
cp .env.example .env

# Edit with your API keys
nano .env
```

Required environment variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `PINECONE_API_KEY` - Your Pinecone API key
- `SECRET_KEY` - A strong secret key (generate with: `openssl rand -hex 32`)

Optional (but recommended for SQL agent):
- Database credentials - defaults work with docker-compose:
  - `DB_HOST=postgres`
  - `DB_PORT=5432`
  - `DB_NAME=customersupport`
  - `DB_USER=postgres`
  - `DB_PASSWORD=postgres`
  
  Or use full connection string:
  - `DATABASE_URL=postgresql://postgres:postgres@postgres:5432/customersupport`

### 3. Start Services

```bash
docker-compose up -d
```

This will start:
- Backend API on port 8000
- Frontend UI on port 3000
- PostgreSQL database on port 5432 (automatically initialized with schema and sample data)

### 4. Verify Installation

- Frontend: http://localhost:3003 (or http://localhost:3000/3001 if available)
- Backend Health: http://localhost:8000/api/v1/health
- API Documentation: http://localhost:8000/docs

### 5. Test Database Connection

The database is automatically initialized with:
- Schema: customers, products, orders, order_items, support_tickets, ticket_messages
- Sample data: 5 customers, 5 products, 5 orders, 5 support tickets

Test the database connection:
```bash
# Using docker-compose
docker-compose exec backend python backend/db/test_connection.py

# Or if running locally
cd backend
python db/test_connection.py
```

You can also test with SQL queries:
```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d customersupport

# Run sample queries
\i backend/db/test_queries.sql
```

### 6. Test the System

1. Open http://localhost:3003 (or http://localhost:3000/3001 if available) in your browser
2. Select an agent (or use "Auto" for automatic routing)
3. Try a query:
   - **RAG**: "What is our return policy?"
   - **SQL**: "How many customers are in the database?"
   - **SQL**: "Show me all open support tickets"
   - **SQL**: "What is the total revenue from orders?"
   - **SQL**: "List customers with their order counts"
   - **Analyzer**: "Analyze our sales trends" (requires data from SQL first)

## Development Mode

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your-key
export PINECONE_API_KEY=your-key
# ... etc

# Run server
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Troubleshooting

### Backend won't start
- Check that all environment variables are set
- Verify API keys are valid
- Check logs: `docker-compose logs backend`

### Frontend can't connect
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Check CORS settings in backend config
- Check browser console for errors

### Pinecone errors
- Verify PINECONE_API_KEY is set correctly
- Check Pinecone index exists or will be created automatically
- Ensure you have sufficient Pinecone credits

### Database connection issues
- Verify DATABASE_URL or individual DB_* variables are set
- Check PostgreSQL is running: `docker-compose ps postgres`
- Test connection: `docker-compose exec postgres psql -U postgres`

## Stopping Services

```bash
docker-compose down
```

To remove volumes (database data):

```bash
docker-compose down -v
```

## Next Steps

- Populate Pinecone with your knowledge base for RAG
- Set up your database schema for SQL queries
- Configure production settings (HTTPS, stronger secrets, etc.)
- Set up monitoring and logging

