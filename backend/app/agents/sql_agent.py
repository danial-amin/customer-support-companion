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
            
            system_prompt = """Vous êtes un expert en traduction de requêtes SQL pour le système de gestion de carburant Total Energies. 
            Traduisez les questions en langage naturel en requêtes SQL pour la base de données de gestion de carburant.
            La base de données contient des tables pour les stations-service, les types de carburant, les véhicules, les cartes carburant, les transactions de carburant, 
            l'inventaire de carburant, les ravitaillements, et les rapports de consommation de carburant.
            Générez uniquement des requêtes SELECT. Ne générez jamais d'instructions INSERT, UPDATE, DELETE, DROP ou ALTER.
            Utilisez le schéma de base de données fourni pour construire des requêtes précises.
            
            RÈGLES CRITIQUES POUR LES REQUÊTES D'AGRÉGATION:
            - Lorsqu'on demande "quelle station a le plus de ventes", "meilleure station", "ventes les plus élevées", etc., vous DEVEZ:
              1. JOIN fuel_transactions avec fuel_stations pour obtenir les noms des stations
              2. Utiliser SUM() ou COUNT() pour agréger les ventes/transactions
              3. Utiliser GROUP BY pour grouper par station
              4. Utiliser ORDER BY ... DESC pour trier par ventes décroissantes
              5. Utiliser LIMIT 1 si on demande "le plus" ou "top 1"
            
            - Lorsqu'on demande "combien", "compter", "total", "somme", "moyenne", vous DEVEZ utiliser des fonctions d'agrégation:
              * COUNT(*) pour compter les enregistrements
              * SUM(column) pour les totaux
              * AVG(column) pour les moyennes
              * GROUP BY lors du regroupement par catégories
            
            - Lorsqu'on demande "top N", "le plus élevé", "le plus bas", "meilleur", "pire", vous DEVEZ:
              * Utiliser ORDER BY avec DESC (pour le plus élevé/meilleur) ou ASC (pour le plus bas/pire)
              * Utiliser LIMIT N pour obtenir les N meilleurs résultats
            
            IMPORTANT: 
            - Retournez toujours une requête SQL SELECT valide, même si l'utilisateur demande des graphiques ou visualisations
            - Pour les demandes de visualisation, générez une requête SQL qui récupère les données nécessaires pour la visualisation
            - Retournez UNIQUEMENT la requête SQL, pas d'explications, pas de formatage markdown, pas de réponses en langage naturel
            - Si vous ne pouvez pas créer une requête, retournez une requête simple comme "SELECT 1" et définissez une erreur à la place
            - Comprenez la terminologie de gestion de carburant: stations-service, types de carburant, véhicules, cartes carburant, transactions, inventaire
            
            EXEMPLES DE REQUÊTES:
            
            Exemple 1 - "Quelle station a le plus de ventes?":
            SELECT fs.name, fs.station_code, SUM(ft.total_amount) as total_sales
            FROM fuel_transactions ft
            JOIN fuel_stations fs ON ft.station_id = fs.id
            GROUP BY fs.id, fs.name, fs.station_code
            ORDER BY total_sales DESC
            LIMIT 1;
            
            Exemple 2 - "Top 5 stations par ventes":
            SELECT fs.name, SUM(ft.total_amount) as total_sales
            FROM fuel_transactions ft
            JOIN fuel_stations fs ON ft.station_id = fs.id
            GROUP BY fs.id, fs.name
            ORDER BY total_sales DESC
            LIMIT 5;
            
            Exemple 3 - "Combien de transactions par station?":
            SELECT fs.name, COUNT(ft.id) as transaction_count
            FROM fuel_stations fs
            LEFT JOIN fuel_transactions ft ON fs.id = ft.station_id
            GROUP BY fs.id, fs.name
            ORDER BY transaction_count DESC;
            
            Exemple 4 - "Total de carburant vendu par station":
            SELECT fs.name, SUM(ft.quantity_liters) as total_liters
            FROM fuel_transactions ft
            JOIN fuel_stations fs ON ft.station_id = fs.id
            GROUP BY fs.id, fs.name
            ORDER BY total_liters DESC;"""
            
            user_prompt = f"""Schéma de base de données:
{schema_json}

Question de l'utilisateur: {state['query']}

Générez une requête SQL SELECT pour récupérer les données nécessaires pour répondre à cette question. 
- Si la question demande "le plus", "top", "le plus élevé", "meilleur", utilisez GROUP BY, fonctions d'agrégation (SUM, COUNT), et ORDER BY DESC avec LIMIT
- Si la question demande "combien", "compter", "total", utilisez COUNT(*) ou SUM() avec GROUP BY approprié
- Toujours JOIN les tables lorsque vous avez besoin de données de plusieurs tables (par ex., noms de stations de fuel_stations, données de transactions de fuel_transactions)
- Même si la question demande un graphique, générez une requête SQL qui récupère les données sous-jacentes
Retournez UNIQUEMENT la requête SQL, rien d'autre."""
            
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
                    state["error"] = "Impossible de générer une requête SQL valide. La demande peut nécessiter des outils d'analyse de données ou de visualisation."
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
                state["answer"] = f"Erreur: {state['error']}"
                return state
            
            if not state.get("result"):
                state["answer"] = "Aucun résultat trouvé."
                return state
            
            result = state["result"]
            rows = result.get("rows", [])
            columns = result.get("columns", [])
            row_count = result.get("row_count", 0)
            original_query = state.get("query", "")
            sql_query = state.get("sql_query", "")
            
            if row_count == 0:
                state["answer"] = "La requête a été exécutée avec succès, mais aucun enregistrement correspondant n'a été trouvé."
                return state
            
            # Format the results for the LLM
            # Serialize rows to ensure all types are JSON-compatible
            serialized_rows = serialize_for_json(rows[:50])  # Limit to first 50 rows for LLM context
            results_text = json.dumps({
                "columns": columns,
                "rows": serialized_rows,
                "total_rows": row_count
            }, indent=2)
            
            system_prompt = """Vous êtes un analyste de données utile pour la gestion de carburant Total Energies. Votre travail est d'interpréter les résultats de requêtes SQL de la base de données de gestion de carburant et de fournir une réponse claire en langage naturel à la question de l'utilisateur.

Votre réponse doit:
1. Répondre directement à la question de l'utilisateur en utilisant les données réelles des résultats de la requête
2. Inclure des chiffres, valeurs et faits spécifiques des résultats (quantités de carburant, prix, noms de stations, immatriculations de véhicules, etc.)
3. Être concise et claire
4. Si la requête a retourné plusieurs lignes, résumez les conclusions clés - surtout pour les requêtes d'agrégation (meilleures stations, ventes les plus élevées, etc.)
5. Si la requête est un COUNT ou agrégation, indiquez le nombre/valeur exact
6. Pour les questions de type "quelle station a le plus de ventes", identifiez le nom de la station et le montant/valeur des ventes à partir des résultats
7. Ne dites pas simplement "la requête a retourné X lignes" - utilisez réellement les données pour répondre à la question
8. Répondez toujours en français

CRITIQUE: Lorsque l'utilisateur demande "quelle station a le plus de ventes" ou des questions de classement similaires:
- Regardez les résultats de la requête pour les noms de stations et les montants des ventes
- Identifiez la station avec la valeur de ventes la plus élevée
- Énoncez clairement: "La station [nom] a le plus de ventes avec [montant]" ou similaire
- Si les résultats de la requête montrent des données agrégées (total_sales, total_amount, etc.), utilisez ces valeurs

Écrivez dans un ton naturel et conversationnel. Utilisez la terminologie de gestion de carburant de manière appropriée."""
            
            user_prompt = f"""Question originale de l'utilisateur: {original_query}

Requête SQL exécutée: {sql_query}

Résultats de la requête:
{results_text}

Basé sur les résultats de la requête ci-dessus, fournissez une réponse claire et directe à la question de l'utilisateur: "{original_query}"

Utilisez les valeurs réelles des données des résultats pour répondre à la question. Soyez spécifique et incluez les chiffres lorsque cela est pertinent. Répondez en français."""
            
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
                state["answer"] = f"Requête exécutée avec succès et a retourné {row_count} ligne(s)."
            else:
                state["answer"] = "Requête exécutée, mais j'ai rencontré une erreur lors du formatage de la réponse."
        
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

