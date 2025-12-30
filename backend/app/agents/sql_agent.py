"""NLP to SQL translation agent."""
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from app.config import settings
from app.services.database_service import database_service
import logging
import json

logger = logging.getLogger(__name__)


class SQLAgentState(TypedDict):
    """State for SQL agent."""
    query: str
    schema: Dict[str, Any]
    sql_query: str
    result: Optional[Dict[str, Any]]
    error: Optional[str]


class SQLAgent:
    """Agent that translates natural language to SQL queries."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=0.1,  # Lower temperature for more deterministic SQL
            api_key=settings.OPENAI_API_KEY
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow for SQL translation."""
        workflow = StateGraph(SQLAgentState)
        
        workflow.add_node("get_schema", self._get_schema)
        workflow.add_node("translate", self._translate_to_sql)
        workflow.add_node("execute", self._execute_sql)
        
        workflow.set_entry_point("get_schema")
        workflow.add_edge("get_schema", "translate")
        workflow.add_edge("translate", "execute")
        workflow.add_edge("execute", END)
        
        return workflow.compile()
    
    def _get_schema(self, state: SQLAgentState) -> SQLAgentState:
        """Get database schema."""
        try:
            if not database_service.is_available():
                state["error"] = "Database service is not available"
                state["schema"] = {}
                return state
            
            schema = database_service.get_schema()
            state["schema"] = schema
            logger.info(f"Retrieved schema for {len(schema)} tables")
        except Exception as e:
            logger.error(f"Error getting schema: {e}")
            state["error"] = str(e)
            state["schema"] = {}
        
        return state
    
    def _translate_to_sql(self, state: SQLAgentState) -> SQLAgentState:
        """Translate natural language query to SQL."""
        try:
            schema_json = json.dumps(state.get("schema", {}), indent=2)
            
            system_prompt = """You are an expert SQL query translator. 
            Translate natural language questions into SQL queries.
            Only generate SELECT queries. Never generate INSERT, UPDATE, DELETE, DROP, or ALTER statements.
            Use the provided database schema to construct accurate queries.
            Return ONLY the SQL query, no explanations or markdown formatting."""
            
            user_prompt = f"""Database Schema:
{schema_json}

User Question: {state['query']}

Generate a SQL SELECT query to answer this question. Return only the SQL query."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            sql_query = response.content.strip()
            
            # Remove markdown code blocks if present
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.startswith("```"):
                sql_query = sql_query[3:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            sql_query = sql_query.strip()
            
            state["sql_query"] = sql_query
            logger.info(f"Generated SQL: {sql_query}")
            
        except Exception as e:
            logger.error(f"Error translating to SQL: {e}")
            state["error"] = str(e)
            state["sql_query"] = ""
        
        return state
    
    def _execute_sql(self, state: SQLAgentState) -> SQLAgentState:
        """Execute the generated SQL query."""
        try:
            if state.get("error") or not state.get("sql_query"):
                return state
            
            if not database_service.is_available():
                state["error"] = "Database service is not available"
                return state
            
            result = database_service.execute_query(state["sql_query"])
            state["result"] = result
            logger.info(f"Query executed successfully, returned {result.get('row_count', 0)} rows")
            
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            state["error"] = str(e)
            state["result"] = None
        
        return state
    
    async def query(self, query: str) -> Dict[str, Any]:
        """Process a natural language query and return SQL results."""
        initial_state: SQLAgentState = {
            "query": query,
            "schema": {},
            "sql_query": "",
            "result": None,
            "error": None
        }
        
        try:
            result = await self.graph.ainvoke(initial_state)
            return {
                "sql_query": result.get("sql_query", ""),
                "result": result.get("result"),
                "error": result.get("error")
            }
        except Exception as e:
            logger.error(f"Error in SQL agent: {e}")
            return {
                "sql_query": "",
                "result": None,
                "error": str(e)
            }


# Global instance - initialize only if API key is available
try:
    if settings.OPENAI_API_KEY:
        sql_agent = SQLAgent()
    else:
        sql_agent = None
        logger.warning("SQL agent not initialized: OPENAI_API_KEY not set")
except Exception as e:
    sql_agent = None
    logger.error(f"Failed to initialize SQL agent: {e}")

