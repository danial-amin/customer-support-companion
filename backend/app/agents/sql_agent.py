"""NLP to SQL translation agent."""
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from app.config import settings
from app.services.database_service import database_service
from app.utils.serialization import serialize_for_json
import logging
import json
import re

logger = logging.getLogger(__name__)


class SQLAgentState(TypedDict):
    """State for SQL agent."""
    query: str
    schema: Dict[str, Any]
    sql_query: str
    result: Optional[Dict[str, Any]]
    answer: Optional[str]
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
        workflow.add_node("format_answer", self._format_answer)
        
        workflow.set_entry_point("get_schema")
        workflow.add_edge("get_schema", "translate")
        workflow.add_edge("translate", "execute")
        workflow.add_edge("execute", "format_answer")
        workflow.add_edge("format_answer", END)
        
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
            
            system_prompt = """You are an expert SQL query translator for Total Energies fuel management system. 
            Translate natural language questions into SQL queries for the fuel management database.
            The database contains tables for fuel stations, fuel types, vehicles, fuel cards, fuel transactions, 
            fuel inventory, fuel refills, and fuel consumption reports.
            Only generate SELECT queries. Never generate INSERT, UPDATE, DELETE, DROP, or ALTER statements.
            Use the provided database schema to construct accurate queries.
            
            CRITICAL RULES FOR AGGREGATION QUERIES:
            - When asked "which station has the most sales", "top station", "highest sales", etc., you MUST:
              1. JOIN fuel_transactions with fuel_stations to get station names
              2. Use SUM() or COUNT() to aggregate sales/transactions
              3. Use GROUP BY to group by station
              4. Use ORDER BY ... DESC to sort by sales descending
              5. Use LIMIT 1 if asking for "the most" or "top 1"
            
            - When asked "how many", "count", "total", "sum", "average", you MUST use aggregation functions:
              * COUNT(*) for counting records
              * SUM(column) for totals
              * AVG(column) for averages
              * GROUP BY when grouping by categories
            
            - When asked "top N", "highest", "lowest", "best", "worst", you MUST:
              * Use ORDER BY with DESC (for highest/best) or ASC (for lowest/worst)
              * Use LIMIT N to get top N results
            
            IMPORTANT: 
            - Always return a valid SQL SELECT query, even if the user asks for charts, graphs, or visualizations
            - For visualization requests, generate a SQL query that retrieves the data needed for the visualization
            - Return ONLY the SQL query, no explanations, no markdown formatting, no natural language responses
            - If you cannot create a query, return a simple query like "SELECT 1" and set an error instead
            - Understand fuel management terminology: fuel stations, fuel types, vehicles, fuel cards, transactions, inventory
            
            EXAMPLE QUERIES:
            
            Example 1 - "Which station has the most sales?":
            SELECT fs.name, fs.station_code, SUM(ft.total_amount) as total_sales
            FROM fuel_transactions ft
            JOIN fuel_stations fs ON ft.station_id = fs.id
            GROUP BY fs.id, fs.name, fs.station_code
            ORDER BY total_sales DESC
            LIMIT 1;
            
            Example 2 - "Top 5 stations by sales":
            SELECT fs.name, SUM(ft.total_amount) as total_sales
            FROM fuel_transactions ft
            JOIN fuel_stations fs ON ft.station_id = fs.id
            GROUP BY fs.id, fs.name
            ORDER BY total_sales DESC
            LIMIT 5;
            
            Example 3 - "How many transactions per station?":
            SELECT fs.name, COUNT(ft.id) as transaction_count
            FROM fuel_stations fs
            LEFT JOIN fuel_transactions ft ON fs.id = ft.station_id
            GROUP BY fs.id, fs.name
            ORDER BY transaction_count DESC;
            
            Example 4 - "Total fuel sold by station":
            SELECT fs.name, SUM(ft.quantity_liters) as total_liters
            FROM fuel_transactions ft
            JOIN fuel_stations fs ON ft.station_id = fs.id
            GROUP BY fs.id, fs.name
            ORDER BY total_liters DESC;"""
            
            user_prompt = f"""Database Schema:
{schema_json}

User Question: {state['query']}

Generate a SQL SELECT query to retrieve the data needed to answer this question. 
- If the question asks about "most", "top", "highest", "best", use GROUP BY, aggregation functions (SUM, COUNT), and ORDER BY DESC with LIMIT
- If the question asks about "how many", "count", "total", use COUNT(*) or SUM() with appropriate GROUP BY
- Always JOIN tables when you need data from multiple tables (e.g., station names from fuel_stations, transaction data from fuel_transactions)
- Even if the question asks for a chart or graph, generate a SQL query that gets the underlying data
Return ONLY the SQL query, nothing else."""
            
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
            
            # Validate that the response is actually SQL, not natural language
            sql_upper = sql_query.upper()
            if not (sql_upper.startswith("SELECT") or sql_upper.startswith("WITH")):
                # If the LLM returned natural language instead of SQL, try to extract SQL or set error
                logger.warning(f"SQL agent returned non-SQL response: {sql_query[:100]}")
                # Try to find SQL in the response
                sql_match = re.search(r'(SELECT\s+.*?)(?:\n|$)', sql_query, re.IGNORECASE | re.DOTALL)
                if sql_match:
                    sql_query = sql_match.group(1).strip()
                    logger.info(f"Extracted SQL from response: {sql_query[:100]}")
                else:
                    # If no SQL found, set an error and use a placeholder query
                    state["error"] = "Could not generate a valid SQL query. The request may require data analysis or visualization tools."
                    state["sql_query"] = "SELECT 1 as error"
                    logger.error(f"Failed to generate SQL query from: {sql_query[:100]}")
                    return state
            
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
    
    def _format_answer(self, state: SQLAgentState) -> SQLAgentState:
        """Generate a natural language answer from SQL results."""
        try:
            if state.get("error"):
                state["answer"] = f"Error: {state['error']}"
                return state
            
            if not state.get("result"):
                state["answer"] = "No results found."
                return state
            
            result = state["result"]
            rows = result.get("rows", [])
            columns = result.get("columns", [])
            row_count = result.get("row_count", 0)
            original_query = state.get("query", "")
            sql_query = state.get("sql_query", "")
            
            if row_count == 0:
                state["answer"] = "The query executed successfully, but no matching records were found."
                return state
            
            # Format the results for the LLM
            # Serialize rows to ensure all types are JSON-compatible
            serialized_rows = serialize_for_json(rows[:50])  # Limit to first 50 rows for LLM context
            results_text = json.dumps({
                "columns": columns,
                "rows": serialized_rows,
                "total_rows": row_count
            }, indent=2)
            
            system_prompt = """You are a helpful fuel management data analyst for Total Energies. Your job is to interpret SQL query results from the fuel management database and provide a clear, natural language answer to the user's question.

Your response should:
1. Directly answer the user's question using the actual data from the query results
2. Include specific numbers, values, and facts from the results (fuel quantities, prices, station names, vehicle registrations, etc.)
3. Be concise and clear
4. If the query returned multiple rows, summarize the key findings - especially for aggregation queries (top stations, highest sales, etc.)
5. If the query is a COUNT or aggregation, state the exact number/value
6. For "which station has the most sales" type questions, identify the station name and the sales amount/value from the results
7. Do not just say "the query returned X rows" - actually use the data to answer the question
8. Always respond in the same language as the user's question (English or French)

CRITICAL: When the user asks "which station has the most sales" or similar ranking questions:
- Look at the query results for station names and sales amounts
- Identify the station with the highest sales value
- State clearly: "Station [name] has the most sales with [amount]" or similar
- If the query results show aggregated data (total_sales, total_amount, etc.), use those values

Write in a natural, conversational tone. Use fuel management terminology appropriately."""
            
            # Detect language from query
            query_lower = original_query.lower()
            is_french = any(word in query_lower for word in ['comment', 'quoi', 'où', 'quand', 'pourquoi', 'combien', 'quel', 'quelle', 'quelles', 'quels', 'montre', 'liste', 'donne'])
            
            if is_french:
                user_prompt = f"""Question originale de l'utilisateur: {original_query}

Requête SQL exécutée: {sql_query}

Résultats de la requête:
{results_text}

Basé sur les résultats de la requête ci-dessus, fournissez une réponse claire et directe à la question de l'utilisateur: "{original_query}"

Utilisez les valeurs réelles des données des résultats pour répondre à la question. Soyez spécifique et incluez les chiffres lorsque cela est pertinent. Répondez en français."""
            else:
                user_prompt = f"""Original User Question: {original_query}

SQL Query Executed: {sql_query}

Query Results:
{results_text}

Based on the query results above, provide a clear, direct answer to the user's question: "{original_query}"

Use the actual data values from the results to answer the question. Be specific and include numbers where relevant. Respond in the same language as the question."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            state["answer"] = response.content.strip()
            logger.info(f"Generated answer from SQL results")
            
        except Exception as e:
            logger.error(f"Error formatting answer: {e}")
            # Fallback to basic answer if LLM fails
            if state.get("result"):
                row_count = state["result"].get("row_count", 0)
                state["answer"] = f"Query executed successfully and returned {row_count} row(s)."
            else:
                state["answer"] = "Query executed, but I encountered an error while formatting the answer."
        
        return state
    
    async def query(self, query: str) -> Dict[str, Any]:
        """Process a natural language query and return SQL results."""
        initial_state: SQLAgentState = {
            "query": query,
            "schema": {},
            "sql_query": "",
            "result": None,
            "answer": None,
            "error": None
        }
        
        try:
            result = await self.graph.ainvoke(initial_state)
            return {
                "sql_query": result.get("sql_query", ""),
                "result": result.get("result"),
                "answer": result.get("answer", ""),
                "error": result.get("error")
            }
        except Exception as e:
            logger.error(f"Error in SQL agent: {e}")
            return {
                "sql_query": "",
                "result": None,
                "answer": "",
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

