# Architecture Documentation

## System Overview

This is a scalable, LLM-based customer support system built with LangGraph for agent orchestration. The system consists of three specialized AI agents that can work independently or together through an intelligent orchestrator.

## Architecture Diagram

```
┌─────────────┐
│   Frontend  │ (React + Vite)
│  Port 3000  │
└──────┬──────┘
       │ HTTP/REST
       │
┌──────▼─────────────────────────────────────┐
│         FastAPI Backend                     │
│         Port 8000                           │
│  ┌──────────────────────────────────────┐   │
│  │      Orchestrator (LangGraph)        │   │
│  │  ┌──────────┐  ┌──────────┐         │   │
│  │  │ RAG Agent│  │ SQL Agent│         │   │
│  │  └────┬─────┘  └────┬─────┘         │   │
│  │       │            │                 │   │
│  │  ┌────▼────────────▼─────┐          │   │
│  │  │   Analyzer Agent       │          │   │
│  │  └───────────────────────┘          │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌──────────────┐  ┌──────────────┐         │
│  │ Pinecone     │  │ Database     │         │
│  │ Service      │  │ Service      │         │
│  └──────────────┘  └──────────────┘         │
└──────┬──────────────────┬───────────────────┘
       │                  │
       │                  │
┌──────▼──────┐  ┌───────▼────────┐
│  Pinecone   │  │  PostgreSQL    │
│  Vector DB  │  │  Database      │
└─────────────┘  └────────────────┘
```

## Components

### Frontend (React + Vite)

**Location**: `frontend/`

**Technologies**:
- React 18
- Vite (build tool)
- Axios (HTTP client)

**Features**:
- Real-time chat interface
- Agent selection UI
- Health status monitoring
- Responsive design
- Modern gradient UI

**Key Components**:
- `App.jsx` - Main application component
- `ChatInterface` - Chat UI
- `AgentSelector` - Agent selection
- `Message` - Message display with metadata
- `StatusIndicator` - Backend health status

### Backend (FastAPI)

**Location**: `backend/app/`

**Technologies**:
- FastAPI (async web framework)
- LangGraph (agent orchestration)
- LangChain (LLM integration)
- Pinecone (vector database)
- SQLAlchemy (database abstraction)
- Pydantic (data validation)

#### API Layer (`api/routes.py`)

**Endpoints**:
- `GET /api/v1/health` - Health check
- `POST /api/v1/query` - Main query endpoint (with auto-routing)
- `POST /api/v1/rag` - Direct RAG agent access
- `POST /api/v1/sql` - Direct SQL agent access
- `POST /api/v1/analyze` - Direct analyzer agent access
- `GET /api/v1/schema` - Database schema information

#### Agents (`agents/`)

**1. RAG Agent** (`rag_agent.py`)
- **Purpose**: Answer questions using retrieved context from Pinecone
- **Workflow**:
  1. Generate embedding for user query
  2. Search Pinecone for similar vectors
  3. Retrieve context documents
  4. Generate answer using LLM with context
- **State**: `RAGState` (query, context, answer, error)

**2. SQL Agent** (`sql_agent.py`)
- **Purpose**: Translate natural language to SQL and execute queries
- **Workflow**:
  1. Get database schema
  2. Translate NL query to SQL using LLM
  3. Execute SQL query safely (read-only)
  4. Return results
- **State**: `SQLAgentState` (query, schema, sql_query, result, error)
- **Safety**: Blocks DROP, DELETE, TRUNCATE, ALTER, CREATE, INSERT, UPDATE

**3. Analyzer Agent** (`analyzer_agent.py`)
- **Purpose**: Analyze data and provide insights
- **Workflow**:
  1. Analyze provided data
  2. Generate insights using LLM
  3. Extract key insights
- **State**: `AnalyzerState` (query, data, analysis, insights, error)

**4. Orchestrator** (`orchestrator.py`)
- **Purpose**: Route queries to appropriate agent(s)
- **Workflow**:
  1. Analyze query to determine best agent(s)
  2. Route to selected agent(s)
  3. Synthesize response
- **Routing Logic**:
  - Uses LLM for intelligent routing
  - Supports hybrid mode (multiple agents)
  - Fallback to RAG for general queries

#### Services (`services/`)

**Pinecone Service** (`pinecone_service.py`)
- Manages Pinecone vector database connection
- Handles vector upserts and queries
- Auto-creates index if missing

**Database Service** (`database_service.py`)
- Manages database connections
- Provides schema introspection
- Executes queries safely
- Connection pooling for scalability

#### Security (`security.py`)

**Features**:
- API key authentication
- JWT token support
- Password hashing (bcrypt)
- Input validation

**Implementation**:
- API key required in `X-API-Key` header
- CORS protection
- SQL injection prevention
- Input sanitization

## Data Flow

### Query Processing Flow

1. **User Input** → Frontend sends query to `/api/v1/query`
2. **Authentication** → API key verified
3. **Orchestration** → Orchestrator determines agent(s)
4. **Agent Execution**:
   - **RAG**: Query Pinecone → Retrieve context → Generate answer
   - **SQL**: Get schema → Translate to SQL → Execute → Return results
   - **Analyzer**: Analyze data → Generate insights
5. **Response Synthesis** → Combine results
6. **Return** → JSON response to frontend

### RAG Flow (Detailed)

```
User Query
    ↓
Generate Embedding (OpenAI)
    ↓
Query Pinecone (Vector Search)
    ↓
Retrieve Top-K Documents
    ↓
Build Context
    ↓
LLM Generation (with context)
    ↓
Return Answer
```

### SQL Flow (Detailed)

```
User Query
    ↓
Get Database Schema
    ↓
LLM Translation (NL → SQL)
    ↓
Safety Check (Read-only)
    ↓
Execute Query
    ↓
Return Results
```

## Scalability Considerations

### Horizontal Scaling

- **Stateless API**: All endpoints are stateless
- **Connection Pooling**: Database connections use pools
- **Async Operations**: All I/O operations are async
- **Container Ready**: Dockerized for easy scaling

### Performance Optimizations

- **Vector Search**: Efficient Pinecone queries
- **Query Caching**: Can be added for frequently asked questions
- **Database Indexing**: Relies on proper DB indexes
- **Connection Reuse**: SQLAlchemy connection pooling

### Resource Management

- **Health Checks**: Built-in health monitoring
- **Error Handling**: Comprehensive error handling
- **Logging**: Structured logging for debugging
- **Resource Limits**: Docker resource limits configurable

## Security Architecture

### Authentication & Authorization

- **API Keys**: Required for all endpoints
- **JWT Support**: Ready for token-based auth
- **CORS**: Configurable origin restrictions

### Input Validation

- **Pydantic Models**: All inputs validated
- **SQL Safety**: Read-only queries enforced
- **Type Checking**: Strong typing throughout

### Infrastructure Security

- **Non-root Containers**: Docker runs as non-root user
- **Secrets Management**: Environment variables (use secrets manager in production)
- **HTTPS Ready**: Configure reverse proxy for production

## Deployment Architecture

### Docker Compose Setup

```
Services:
├── backend (FastAPI)
├── frontend (Nginx)
└── postgres (Optional)
```

### Production Considerations

1. **Reverse Proxy**: Use nginx/traefik for HTTPS
2. **Secrets Management**: Use AWS Secrets Manager, HashiCorp Vault, etc.
3. **Monitoring**: Add Prometheus/Grafana
4. **Logging**: Centralized logging (ELK stack)
5. **Load Balancing**: Multiple backend instances
6. **Database**: Managed PostgreSQL service
7. **CDN**: For frontend static assets

## Technology Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | React + Vite | User interface |
| Backend | FastAPI | API server |
| Orchestration | LangGraph | Agent workflows |
| LLM | OpenAI GPT-4 | Language model |
| Vector DB | Pinecone | RAG storage |
| Database | PostgreSQL | SQL queries |
| Container | Docker | Deployment |
| Security | JWT, API Keys | Authentication |

## Extension Points

### Adding New Agents

1. Create agent file in `agents/`
2. Define state using TypedDict
3. Build LangGraph workflow
4. Add to orchestrator routing
5. Create API endpoint

### Adding New Services

1. Create service file in `services/`
2. Initialize in service module
3. Use in agents or API routes

### Customizing Security

1. Update `security.py` with custom logic
2. Modify API key validation
3. Add rate limiting
4. Implement user management

## Monitoring & Observability

### Health Checks

- Backend: `/api/v1/health`
- Frontend: HTTP status check
- Database: Connection test
- Pinecone: Availability check

### Logging

- Structured logging throughout
- Error tracking
- Request/response logging (can be added)

### Metrics (To Add)

- Request count
- Response times
- Error rates
- Agent usage statistics

