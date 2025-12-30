"""API routes for the application."""
from fastapi import APIRouter, HTTPException, Depends, Security
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.agents.rag_agent import rag_agent
from app.agents.sql_agent import sql_agent
from app.agents.analyzer_agent import analyzer_agent
from app.agents.orchestrator import orchestrator
from app.security import verify_api_key
from app.services.pinecone_service import pinecone_service
from app.services.database_service import database_service
from app.services.document_service import document_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    query: str = Field(..., description="The user's query")
    agent_type: Optional[str] = Field(None, description="Specific agent to use (rag, sql, analyzer, auto)")


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    answer: str
    agent_used: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class RAGQueryRequest(BaseModel):
    """Request model for RAG query."""
    query: str = Field(..., description="The question to answer")


class RAGQueryResponse(BaseModel):
    """Response model for RAG query."""
    answer: str
    context_sources: int
    error: Optional[str] = None


class SQLQueryRequest(BaseModel):
    """Request model for SQL query."""
    query: str = Field(..., description="Natural language query to translate to SQL")


class SQLQueryResponse(BaseModel):
    """Response model for SQL query."""
    sql_query: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AnalyzerRequest(BaseModel):
    """Request model for analyzer."""
    query: str = Field(..., description="Analysis request")
    data: Optional[Dict[str, Any]] = Field(None, description="Optional data to analyze")


class AnalyzerResponse(BaseModel):
    """Response model for analyzer."""
    analysis: str
    insights: List[str]
    python_code: Optional[str] = None
    execution_result: Optional[str] = None
    visualization: Optional[str] = None  # Base64 encoded image
    sql_query: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    services: Dict[str, bool]


class DocumentIngestRequest(BaseModel):
    """Request model for document ingestion."""
    text: str = Field(..., description="The document text to ingest")
    source: Optional[str] = Field(None, description="Source identifier (e.g., filename, URL)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    namespace: Optional[str] = Field(None, description="Pinecone namespace")


class DocumentIngestResponse(BaseModel):
    """Response model for document ingestion."""
    success: bool
    chunks_ingested: int
    source: Optional[str] = None
    error: Optional[str] = None


# Routes
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "pinecone": pinecone_service.is_available(),
            "database": database_service.is_available()
        }
    }


@router.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    api_key: bool = Security(verify_api_key)
):
    """
    Main query endpoint that routes to appropriate agent.
    """
    try:
        if request.agent_type and request.agent_type != "auto":
            # Use specific agent
            if request.agent_type == "rag":
                if rag_agent is None:
                    raise HTTPException(status_code=503, detail="RAG agent is not available. Please check OPENAI_API_KEY configuration.")
                result = await rag_agent.query(request.query)
                return QueryResponse(
                    answer=result.get("answer", ""),
                    agent_used="rag",
                    error=result.get("error"),
                    metadata={"context_sources": result.get("context_sources", 0)}
                )
            elif request.agent_type == "sql":
                if sql_agent is None:
                    raise HTTPException(status_code=503, detail="SQL agent is not available. Please check OPENAI_API_KEY configuration.")
                result = await sql_agent.query(request.query)
                
                # Format SQL results - simplified since table will be displayed
                answer_parts = [f"SQL Query: {result.get('sql_query', '')}"]
                if result.get("result"):
                    data = result["result"]
                    row_count = data.get('row_count', 0)
                    
                    if row_count == 0:
                        answer_parts.append("\nNo rows found.")
                    else:
                        answer_parts.append(f"\nFound {row_count} row(s). See results table below.")
                
                return QueryResponse(
                    answer="\n".join(answer_parts),
                    agent_used="sql",
                    error=result.get("error"),
                    metadata={
                        "sql_query": result.get("sql_query"), 
                        "result": result.get("result"),
                        "sql_result": result  # Include full result for table display
                    }
                )
            elif request.agent_type == "analyzer":
                if analyzer_agent is None:
                    raise HTTPException(status_code=503, detail="Analyzer agent is not available. Please check OPENAI_API_KEY configuration.")
                result = await analyzer_agent.analyze(request.query)
                
                # Format analyzer response
                answer_parts = [result.get("analysis", "")]
                if result.get("python_code"):
                    answer_parts.append(f"\n\nPython Code Executed:\n```python\n{result['python_code']}\n```")
                if result.get("execution_result"):
                    answer_parts.append(f"\nExecution Results:\n{result['execution_result']}")
                if result.get("visualization"):
                    answer_parts.append("\n[Visualization generated - see metadata]")
                
                return QueryResponse(
                    answer="\n".join(answer_parts),
                    agent_used="analyzer",
                    error=result.get("error"),
                    metadata={
                        "insights": result.get("insights", []),
                        "python_code": result.get("python_code"),
                        "execution_result": result.get("execution_result"),
                        "visualization": result.get("visualization") or result.get("plot_base64"),
                        "sql_query": result.get("sql_query")
                    }
                )
            else:
                raise HTTPException(status_code=400, detail=f"Unknown agent type: {request.agent_type}")
        else:
            # Use orchestrator for automatic routing
            if orchestrator is None:
                raise HTTPException(status_code=503, detail="Orchestrator is not available. Please check OPENAI_API_KEY configuration.")
            result = await orchestrator.process_query(request.query)
            
            # Build metadata with SQL results for table display
            metadata = {
                "rag_result": result.get("rag_result"),
                "sql_result": result.get("sql_result"),
                "analyzer_result": result.get("analyzer_result")
            }
            
            # If SQL was used, include the result data for table display
            if result.get("sql_result") and result.get("sql_result").get("result"):
                metadata["result"] = result.get("sql_result").get("result")
                metadata["sql_query"] = result.get("sql_result").get("sql_query")
            
            # If analyzer was used, extract all analyzer metadata
            if result.get("analyzer_result"):
                analyzer_data = result.get("analyzer_result")
                metadata["python_code"] = analyzer_data.get("python_code")
                metadata["execution_result"] = analyzer_data.get("execution_result")
                # Check both 'visualization' and 'plot_base64' for compatibility
                metadata["visualization"] = analyzer_data.get("visualization") or analyzer_data.get("plot_base64")
                metadata["insights"] = analyzer_data.get("insights", [])
                metadata["sql_query"] = analyzer_data.get("sql_query") or metadata.get("sql_query")
                # Debug logging
                if metadata.get("visualization"):
                    logger.info(f"Analyzer visualization found in metadata ({len(metadata['visualization'])} chars)")
                else:
                    logger.warning("No visualization found in analyzer result")
            
            return QueryResponse(
                answer=result.get("answer", ""),
                agent_used=result.get("agent_used", "auto"),
                error=result.get("error"),
                metadata=metadata
            )
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag", response_model=RAGQueryResponse)
async def rag_query(
    request: RAGQueryRequest,
    api_key: bool = Security(verify_api_key)
):
    """Query the RAG agent directly."""
    if rag_agent is None:
        raise HTTPException(status_code=503, detail="RAG agent is not available. Please check OPENAI_API_KEY configuration.")
    try:
        result = await rag_agent.query(request.query)
        return RAGQueryResponse(
            answer=result.get("answer", ""),
            context_sources=result.get("context_sources", 0),
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sql", response_model=SQLQueryResponse)
async def sql_query(
    request: SQLQueryRequest,
    api_key: bool = Security(verify_api_key)
):
    """Query the SQL agent directly."""
    if sql_agent is None:
        raise HTTPException(status_code=503, detail="SQL agent is not available. Please check OPENAI_API_KEY configuration.")
    try:
        result = await sql_agent.query(request.query)
        return SQLQueryResponse(
            sql_query=result.get("sql_query", ""),
            result=result.get("result"),
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"Error in SQL query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=AnalyzerResponse)
async def analyze(
    request: AnalyzerRequest,
    api_key: bool = Security(verify_api_key)
):
    """Query the analyzer agent directly."""
    if analyzer_agent is None:
        raise HTTPException(status_code=503, detail="Analyzer agent is not available. Please check OPENAI_API_KEY configuration.")
    try:
        result = await analyzer_agent.analyze(request.query, request.data)
        return AnalyzerResponse(
            analysis=result.get("analysis", ""),
            insights=result.get("insights", []),
            python_code=result.get("python_code"),
            execution_result=result.get("execution_result"),
            visualization=result.get("visualization"),
            sql_query=result.get("sql_query"),
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"Error in analyzer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/ingest", response_model=DocumentIngestResponse)
async def ingest_document(
    request: DocumentIngestRequest,
    api_key: bool = Security(verify_api_key)
):
    """Ingest a document into the RAG system."""
    try:
        if not pinecone_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Pinecone service is not available. Please check PINECONE_API_KEY configuration."
            )
        
        result = document_service.ingest_document(
            text=request.text,
            source=request.source,
            metadata=request.metadata,
            namespace=request.namespace
        )
        
        if result.get("success"):
            return DocumentIngestResponse(
                success=True,
                chunks_ingested=result.get("chunks_ingested", 0),
                source=result.get("source")
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to ingest document")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema")
async def get_schema(api_key: bool = Security(verify_api_key)):
    """Get database schema."""
    try:
        schema = database_service.get_schema()
        return {"schema": schema}
    except Exception as e:
        logger.error(f"Error getting schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))

