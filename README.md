# Customer Support AI

A scalable LLM-based customer support tool built with LangGraph, featuring three specialized agents: RAG (Retrieval Augmented Generation), NLP-to-SQL translation, and Data Analysis.

## Architecture

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **LangGraph** - Agent orchestration and workflow management
- **Pinecone** - Vector database for RAG
- **SQLAlchemy** - Database abstraction layer
- **Security** - API key authentication, CORS, input validation

### Frontend
- **React** - Modern UI framework
- **Vite** - Fast build tool
- **Axios** - HTTP client

### Agents

1. **RAG Agent** - Retrieves relevant context from Pinecone vector database and generates answers
2. **SQL Agent** - Translates natural language queries to SQL and executes them safely
3. **Analyzer Agent** - Analyzes data and provides insights
4. **Orchestrator** - Routes queries to the appropriate agent(s) automatically

## Features

- 🤖 Three specialized AI agents
- 🔄 Automatic query routing
- 🔒 Security-first design
- 🐳 Dockerized deployment
- 📊 Real-time health monitoring
- 🎨 Modern, responsive UI
- 🔍 SQL query safety checks
- 📈 Data analysis capabilities

## Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Pinecone API key (for RAG agent)
- PostgreSQL (included in docker-compose, optional for SQL agent)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd customer-support
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```bash
# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Pinecone
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=customer-support

# Database (optional)
DATABASE_URL=postgresql://user:password@postgres:5432/customersupport
# OR
DB_HOST=postgres
DB_PORT=5432
DB_NAME=customersupport
DB_USER=postgres
DB_PASSWORD=postgres

# Security
SECRET_KEY=your-strong-secret-key-here
```

### 3. Run with Docker Compose

```bash
docker-compose up -d
```

This will start:
- Backend API on `http://localhost:8000`
- Frontend UI on `http://localhost:3003` (or `3000`/`3001` if available)
- PostgreSQL database on `localhost:5433` (externally, `5432` internally) - automatically initialized with schema and sample data

**Note**: Ports may be adjusted automatically if conflicts are detected:
- Frontend: Uses port `3003` externally if `3000`/`3001` are in use
- Database: Uses port `5433` externally if `5432` is in use
- Containers communicate internally using standard ports

### 4. Access the Application

- Frontend: http://localhost:3003 (or http://localhost:3000/3001 if available)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your credentials

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Main Query Endpoint
```
POST /api/v1/query
Body: {
  "query": "your question",
  "agent_type": "auto" | "rag" | "sql" | "analyzer"
}
```

### Agent-Specific Endpoints
- `POST /api/v1/rag` - RAG agent
- `POST /api/v1/sql` - SQL agent
- `POST /api/v1/analyze` - Analyzer agent
- `GET /api/v1/health` - Health check
- `GET /api/v1/schema` - Database schema

## Security Features

- API key authentication
- Input validation and sanitization
- SQL injection prevention (read-only queries)
- CORS configuration
- Security headers
- Non-root Docker containers

## Scalability Considerations

- Stateless API design
- Connection pooling
- Async/await for I/O operations
- Horizontal scaling support
- Health checks for orchestration
- Efficient vector search
- Database query optimization

## Deployment

### Railway Deployment (Recommended)

Deploy to Railway in minutes with automatic HTTPS, database provisioning, and zero-config deployments.

**Quick Start:**
1. See [RAILWAY_QUICKSTART.md](./RAILWAY_QUICKSTART.md) for 5-minute deployment
2. See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for detailed guide

**Key Steps:**
- Connect GitHub repo to Railway
- Add PostgreSQL service
- Set environment variables
- Initialize database with `backend/db/init_fuel_management.sql`
- Generate public URLs

### Production Deployment (Docker)

1. **Update environment variables** with production values
2. **Set strong SECRET_KEY** for JWT tokens
3. **Configure CORS_ORIGINS** with your domain
4. **Use environment-specific database** credentials
5. **Enable HTTPS** (use reverse proxy like nginx)
6. **Set up monitoring** and logging
7. **Configure resource limits** in docker-compose

### Example Production docker-compose

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Database Schema

The PostgreSQL database is automatically initialized with a complete schema for customer support operations:

### Tables
- **customers** - Customer information and contact details
- **products** - Product catalog with pricing and inventory
- **orders** - Customer orders with status tracking
- **order_items** - Order line items
- **support_tickets** - Customer support tickets with priority and status
- **ticket_messages** - Ticket conversation history

### Views
- **order_summary** - Aggregated order information
- **ticket_stats** - Ticket statistics by status and priority

### Sample Data
The database includes sample data:
- 5 customers
- 5 products
- 5 orders with order items
- 5 support tickets with messages

See `backend/db/README.md` for detailed schema documentation and example queries.

## Project Structure

```
customer-support/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph agents
│   │   ├── api/              # FastAPI routes
│   │   ├── services/         # External service integrations
│   │   ├── config.py         # Configuration
│   │   ├── security.py       # Authentication
│   │   └── main.py           # FastAPI app
│   ├── db/
│   │   ├── init.sql          # Database initialization script
│   │   ├── test_queries.sql  # Example SQL queries
│   │   └── test_connection.py # Database connection test
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API client
│   │   └── App.jsx
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

