"""Orchestrator for routing queries to appropriate agents."""
from typing import Dict, Any, Optional, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from app.config import settings
from app.agents.rag_agent import rag_agent
from app.agents.sql_agent import sql_agent
from app.agents.analyzer_agent import analyzer_agent
from app.utils.language_detection import detect_language
import logging

logger = logging.getLogger(__name__)


class OrchestratorState(TypedDict):
    """State for orchestrator."""
    query: str
    agent_type: Optional[Literal["rag", "sql", "analyzer", "hybrid"]]
    rag_result: Optional[Dict[str, Any]]
    sql_result: Optional[Dict[str, Any]]
    analyzer_result: Optional[Dict[str, Any]]
    final_answer: str
    error: Optional[str]


class Orchestrator:
    """Orchestrator that routes queries to appropriate agents."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=0.3,  # Lower temperature for routing decisions
            api_key=settings.OPENAI_API_KEY
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow for orchestration."""
        workflow = StateGraph(OrchestratorState)
        
        workflow.add_node("route", self._route_query)
        workflow.add_node("rag", self._call_rag)
        workflow.add_node("sql", self._call_sql)
        workflow.add_node("analyzer", self._call_analyzer)
        workflow.add_node("hybrid", self._call_hybrid)
        workflow.add_node("synthesize", self._synthesize_response)
        
        workflow.set_entry_point("route")
        
        # Conditional routing
        workflow.add_conditional_edges(
            "route",
            self._route_decision,
            {
                "rag": "rag",
                "sql": "sql",
                "analyzer": "analyzer",
                "hybrid": "hybrid"
            }
        )
        
        workflow.add_edge("rag", "synthesize")
        workflow.add_edge("sql", "synthesize")
        workflow.add_edge("analyzer", "synthesize")
        workflow.add_edge("hybrid", "synthesize")
        workflow.add_edge("synthesize", END)
        
        return workflow.compile()
    
    def _route_query(self, state: OrchestratorState) -> OrchestratorState:
        """Route query to appropriate agent(s)."""
        try:
            query = state["query"].lower()
            
            # Simple keyword-based routing (can be enhanced with LLM)
            sql_keywords = ["sql", "query", "database", "table", "select", "count", "sum", "average", "how many", "list", "show me", "get"]
            analyzer_keywords = [
                "analyze", "analysis", "insight", "insights", "trend", "trends", "pattern", "patterns", 
                "statistic", "statistics", "summary", "summarize", "compare", "comparison", "distribution",
                "chart", "graph", "plot", "visualize", "visualization", "bar chart", "line chart", 
                "histogram", "top", "bottom", "highest", "lowest", "best", "worst", "rank", "ranking",
                "percentage", "ratio", "growth", "change", "over time", "by month", "by year"
            ]
            rag_keywords = ["what", "how", "why", "explain", "tell me", "information", "help"]
            
            has_sql = any(keyword in query for keyword in sql_keywords)
            has_analyzer = any(keyword in query for keyword in analyzer_keywords)
            has_rag = any(keyword in query for keyword in rag_keywords) or not (has_sql or has_analyzer)
            
            # Use LLM for more sophisticated routing
            system_prompt = """Determine the best agent(s) to handle this query.
            Options: 'rag' (general knowledge/questions), 'sql' (database queries), 
            'analyzer' (data analysis), 'hybrid' (needs multiple agents).
            Return only the agent type."""
            
            routing_prompt = f"""Query: "{state['query']}"
            
            Determine the best agent to handle this query for Total Energies fuel management system:
            
            - 'rag': General knowledge questions, fuel management policies, "how to" questions, information about fuel stations, fuel types, fuel cards, or vehicle management
              Examples: "What fuel types are available?", "How do I use a fuel card?", "Tell me about fuel station locations", 
                        "What is the fuel pricing policy?", "How do I report a fuel station issue?"
            
            - 'sql': Simple data retrieval, counting, listing records from fuel management database
              Examples: "How many fuel stations do we have?", "List all fuel transactions", "Show me vehicles in Paris",
                        "How many fuel cards are active?", "What is the current fuel inventory at station X?"
            
            - 'analyzer': Data analysis, statistics, comparisons, trends, visualizations, aggregations for fuel management
              Examples: "Analyze fuel consumption trends", "Compare fuel costs by month", "Show me a chart of fuel transactions over time",
                        "What are the top 5 fuel stations by sales?", "Calculate average fuel consumption per vehicle", 
                        "Show distribution of fuel inventory levels", "Analyze fuel efficiency by vehicle type"
            
            - 'hybrid': Complex queries that need both data retrieval and analysis
              Examples: "Get fuel transaction data and analyze consumption patterns", "Retrieve vehicle data and analyze fuel efficiency trends"
            
            Return only: rag, sql, analyzer, or hybrid"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=routing_prompt)
            ]
            
            response = self.llm.invoke(messages)
            agent_type = response.content.strip().lower()
            
            # Validate and fallback
            if agent_type not in ["rag", "sql", "analyzer", "hybrid"]:
                if has_sql and has_analyzer:
                    agent_type = "hybrid"
                elif has_sql:
                    agent_type = "sql"
                elif has_analyzer:
                    agent_type = "analyzer"
                else:
                    agent_type = "rag"
            
            state["agent_type"] = agent_type
            logger.info(f"Routed query to: {agent_type}")
            
        except Exception as e:
            logger.error(f"Error routing query: {e}")
            state["agent_type"] = "rag"  # Default fallback
            state["error"] = str(e)
        
        return state
    
    def _route_decision(self, state: OrchestratorState) -> str:
        """Decision function for routing."""
        return state.get("agent_type", "rag")
    
    async def _call_rag(self, state: OrchestratorState) -> OrchestratorState:
        """Call RAG agent."""
        try:
            result = await rag_agent.query(state["query"])
            state["rag_result"] = result
        except Exception as e:
            logger.error(f"Error in RAG agent: {e}")
            state["rag_result"] = {"error": str(e)}
        return state
    
    async def _call_sql(self, state: OrchestratorState) -> OrchestratorState:
        """Call SQL agent."""
        try:
            result = await sql_agent.query(state["query"])
            state["sql_result"] = result
        except Exception as e:
            logger.error(f"Error in SQL agent: {e}")
            state["sql_result"] = {"error": str(e)}
        return state
    
    async def _call_analyzer(self, state: OrchestratorState) -> OrchestratorState:
        """Call analyzer agent."""
        try:
            # Analyzer will automatically fetch data from SQL if needed
            result = await analyzer_agent.analyze(state["query"])
            state["analyzer_result"] = result
        except Exception as e:
            logger.error(f"Error in analyzer agent: {e}")
            state["analyzer_result"] = {"error": str(e)}
        return state
    
    async def _call_hybrid(self, state: OrchestratorState) -> OrchestratorState:
        """Call multiple agents in sequence."""
        try:
            # First try SQL to get data
            sql_result = await sql_agent.query(state["query"])
            state["sql_result"] = sql_result
            
            # Then analyze the results
            if sql_result.get("result") and not sql_result.get("error"):
                analyzer_result = await analyzer_agent.analyze(
                    state["query"],
                    data=sql_result["result"]
                )
                state["analyzer_result"] = analyzer_result
            else:
                # Fallback to RAG if SQL fails
                rag_result = await rag_agent.query(state["query"])
                state["rag_result"] = rag_result
                
        except Exception as e:
            logger.error(f"Error in hybrid agent: {e}")
            state["error"] = str(e)
        
        return state
    
    def _synthesize_response(self, state: OrchestratorState) -> OrchestratorState:
        """Synthesize final response from agent results."""
        try:
            agent_type = state.get("agent_type", "rag")
            query = state.get("query", "")
            detected_lang = detect_language(query)
            is_french = detected_lang == "fr"
            
            if agent_type == "rag":
                result = state.get("rag_result", {})
                answer = result.get("answer", "")
                if not answer:
                    answer = "Je n'ai pas pu trouver de réponse." if is_french else "I couldn't find an answer."
                state["final_answer"] = answer
            
            elif agent_type == "sql":
                result = state.get("sql_result", {})
                if result.get("error"):
                    error_msg = result['error']
                    state["final_answer"] = f"Erreur: {error_msg}" if is_french else f"Error: {error_msg}"
                elif result.get("answer"):
                    # Use the answer generated by the SQL agent from the actual query results
                    state["final_answer"] = result["answer"]
                elif result.get("result"):
                    # Fallback if answer generation failed
                    row_count = result["result"].get('row_count', 0)
                    if row_count == 0:
                        state["final_answer"] = "La requête a été exécutée avec succès, mais aucune ligne n'a été trouvée." if is_french else "Query executed successfully, but no rows were found."
                    else:
                        state["final_answer"] = f"Requête exécutée avec succès. {row_count} ligne(s) trouvée(s). Voir le tableau des résultats ci-dessous." if is_french else f"Query executed successfully. Found {row_count} row(s). See results table below."
                else:
                    state["final_answer"] = "Aucun résultat trouvé." if is_french else "No results found."
            
            elif agent_type == "analyzer":
                result = state.get("analyzer_result", {})
                if result.get("error"):
                    error_msg = result['error']
                    state["final_answer"] = f"Erreur: {error_msg}" if is_french else f"Error: {error_msg}"
                else:
                    answer_parts = [result.get("analysis", "Analyse terminée." if is_french else "Analysis completed.")]
                    if result.get("python_code"):
                        answer_parts.append(f"\n\nCode Python:\n```python\n{result['python_code']}\n```" if is_french else f"\n\nPython Code:\n```python\n{result['python_code']}\n```")
                    if result.get("execution_result"):
                        answer_parts.append(f"\nRésultats:\n{result['execution_result']}" if is_french else f"\nResults:\n{result['execution_result']}")
                    if result.get("visualization"):
                        answer_parts.append("\n[Visualisation générée]" if is_french else "\n[Visualization generated]")
                    state["final_answer"] = "\n".join(answer_parts)
            
            elif agent_type == "hybrid":
                sql_result = state.get("sql_result", {})
                analyzer_result = state.get("analyzer_result", {})
                
                if analyzer_result.get("analysis"):
                    state["final_answer"] = analyzer_result["analysis"]
                elif sql_result.get("result"):
                    state["final_answer"] = f"Données récupérées: {sql_result['result']}" if is_french else f"Data retrieved: {sql_result['result']}"
                else:
                    state["final_answer"] = "Impossible de terminer l'analyse." if is_french else "Could not complete the analysis."
            
        except Exception as e:
            logger.error(f"Error synthesizing response: {e}")
            state["error"] = str(e)
            detected_lang = detect_language(state.get("query", ""))
            is_french = detected_lang == "fr"
            state["final_answer"] = "Une erreur s'est produite lors du traitement de votre demande." if is_french else "An error occurred while processing your request."
        
        return state
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query through the orchestrator."""
        initial_state: OrchestratorState = {
            "query": query,
            "agent_type": None,
            "rag_result": None,
            "sql_result": None,
            "analyzer_result": None,
            "final_answer": "",
            "error": None
        }
        
        try:
            result = await self.graph.ainvoke(initial_state)
            return {
                "answer": result.get("final_answer", ""),
                "agent_used": result.get("agent_type", "rag"),
                "rag_result": result.get("rag_result"),
                "sql_result": result.get("sql_result"),
                "analyzer_result": result.get("analyzer_result"),
                "error": result.get("error")
            }
        except Exception as e:
            logger.error(f"Error in orchestrator: {e}")
            return {
                "answer": "",
                "agent_used": "error",
                "error": str(e)
            }


# Global instance - initialize only if API key is available
try:
    if settings.OPENAI_API_KEY:
        orchestrator = Orchestrator()
    else:
        orchestrator = None
        logger.warning("Orchestrator not initialized: OPENAI_API_KEY not set")
except Exception as e:
    orchestrator = None
    logger.error(f"Failed to initialize Orchestrator: {e}")

