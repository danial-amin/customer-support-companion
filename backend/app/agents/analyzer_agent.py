"""Data analyzer agent for analyzing query results and data."""
from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from app.config import settings
from app.agents.sql_agent import sql_agent
import logging
import json
import sys
import re
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import base64
from io import BytesIO, StringIO
from app.utils.serialization import serialize_for_json

logger = logging.getLogger(__name__)


class AnalyzerState(TypedDict):
    """State for analyzer agent."""
    query: str
    sql_query: Optional[str]
    data: Optional[Dict[str, Any]]
    python_code: Optional[str]
    execution_result: Optional[str]
    visualization: Optional[str]  # Base64 encoded image
    analysis: str
    insights: List[str]
    error: Optional[str]


class AnalyzerAgent:
    """Agent for analyzing data using Python code execution."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow for data analysis."""
        workflow = StateGraph(AnalyzerState)
        
        workflow.add_node("get_data", self._get_data)
        workflow.add_node("generate_code", self._generate_code)
        workflow.add_node("execute_code", self._execute_code)
        workflow.add_node("analyze_results", self._analyze_results)
        
        workflow.set_entry_point("get_data")
        workflow.add_edge("get_data", "generate_code")
        workflow.add_edge("generate_code", "execute_code")
        workflow.add_edge("execute_code", "analyze_results")
        workflow.add_edge("analyze_results", END)
        
        return workflow.compile()
    
    async def _get_data(self, state: AnalyzerState) -> AnalyzerState:
        """Get data from SQL if not provided."""
        try:
            # If data is already provided, skip SQL query
            if state.get("data"):
                return state
            
            # Otherwise, try to get data from SQL
            if sql_agent is None:
                state["error"] = "SQL agent is not available. Cannot fetch data for analysis."
                return state
            
            # First, try to understand what data is needed from the query
            # Extract key entities and metrics from the query
            query = state["query"]
            
            # Use SQL agent to get data - pass the original query
            # The SQL agent should understand what data to fetch
            sql_result = await sql_agent.query(query)
            
            # Check if SQL agent returned an error
            if sql_result.get("error"):
                error_msg = sql_result.get("error", "Erreur inconnue")
                # Check if the error indicates the SQL agent couldn't generate a query
                if "Could not generate a valid SQL query" in error_msg or "not capable" in error_msg.lower() or "Impossible de générer" in error_msg:
                    state["error"] = f"Impossible d'analyser cette demande: {error_msg}. Veuillez reformuler votre requête pour demander des données qui peuvent être récupérées de la base de données."
                else:
                    state["error"] = f"Échec de la récupération des données pour l'analyse: {error_msg}. Veuillez vous assurer que votre requête fait référence à des tables et colonnes de base de données valides."
                logger.warning(f"SQL agent failed: {error_msg}")
                return state
            
            # Validate that we got a proper SQL query
            sql_query = sql_result.get("sql_query", "")
            if not sql_query or not sql_query.upper().startswith("SELECT"):
                state["error"] = "L'agent SQL n'a pas généré une requête SQL valide. Veuillez reformuler votre demande pour demander des données de la base de données."
                logger.warning(f"Invalid SQL query from SQL agent: {sql_query[:100]}")
                return state
            
            if sql_result.get("result"):
                data = sql_result["result"]
                rows = data.get("rows", [])
                if not rows or len(rows) == 0:
                    state["error"] = "Aucune donnée trouvée pour l'analyse. La requête a retourné des résultats vides."
                    return state
                state["data"] = data
                state["sql_query"] = sql_query
                logger.info(f"Retrieved {len(rows)} rows for analysis")
            else:
                state["error"] = "Aucune donnée récupérée de la requête SQL. Veuillez vérifier votre requête et réessayer."
            
        except Exception as e:
            logger.error(f"Error getting data: {e}", exc_info=True)
            state["error"] = f"Error fetching data: {str(e)}"
        
        return state
    
    def _generate_code(self, state: AnalyzerState) -> AnalyzerState:
        """Generate Python code to analyze the data."""
        try:
            if state.get("error") or not state.get("data"):
                return state
            
            data = state["data"]
            rows = data.get("rows", [])
            columns = data.get("columns", [])
            
            if not rows or not columns:
                state["error"] = "Aucune ligne de données à analyser"
                return state
            
            # Convert to DataFrame format for code generation
            # Serialize non-JSON types (date, datetime, Decimal, UUID, etc.) to strings
            serialized_rows = serialize_for_json(rows[:10])
            data_sample = json.dumps(serialized_rows, indent=2)  # Sample for context
            
            # Check if visualization is requested
            query_lower = state['query'].lower()
            visualization_keywords = ['chart', 'graph', 'plot', 'visualize', 'visualization', 'bar', 'line', 'histogram', 'pie', 'scatter']
            needs_visualization = any(keyword in query_lower for keyword in visualization_keywords)
            
            system_prompt = """Vous êtes un expert analyste de données pour la gestion de carburant Total Energies. Votre travail est de comprendre la demande d'analyse de l'utilisateur pour les données de gestion de carburant et de générer du code Python pour effectuer cette analyse.

COMPRENDRE LA DEMANDE:
- Lisez attentivement la requête de l'utilisateur pour comprendre quelle analyse il souhaite pour les données de gestion de carburant
- Types d'analyse courants pour la gestion de carburant:
  * Résumés statistiques: "montrer les statistiques", "décrire les données", "résumé" (pour transactions de carburant, consommation, inventaire)
  * Agrégations: "total", "moyenne", "compter", "somme", "grouper par" (consommation de carburant, coûts, transactions par station/véhicule)
  * Comparaisons: "comparer", "différence", "lequel est plus élevé" (coûts de carburant, consommation entre stations/véhicules/départements)
  * Tendances: "au fil du temps", "par mois", "tendance" (tendances de consommation de carburant, tendances de prix, volume de transactions)
  * Distributions: "distribution", "histogramme", "fréquence" (niveaux d'inventaire de carburant, montants de transactions)
  * Visualisations: "graphique", "diagramme", "tracer", "visualiser", "graphique en barres", "graphique linéaire" (graphiques de consommation de carburant, performance des stations)
  * Classements: "top", "bas", "le plus élevé", "le plus bas", "meilleur", "pire" (meilleures stations-service, véhicules les plus économes en carburant)
  * Calculs: "pourcentage", "ratio", "croissance", "changement" (efficacité énergétique, coût par kilomètre, utilisation de l'inventaire)

EXIGENCES DU CODE:
1. TOUJOURS commencer par créer un DataFrame: df = pd.DataFrame(data_rows)
2. Comprendre la structure des données - vérifier les colonnes et types de données
3. Effectuer l'analyse demandée
4. TOUJOURS utiliser des instructions print() pour afficher TOUS les résultats, statistiques et conclusions
5. **SI L'UTILISATEUR DEMANDE UN GRAPHIQUE, DIAGRAMME OU TRACE, VOUS DEVEZ EN CRÉER UN**

RÈGLES CRITIQUES POUR LES VISUALISATIONS:
- Lorsqu'une visualisation est demandée, vous DEVEZ créer un graphique matplotlib
- N'utilisez PAS plt.show() - cela causera des erreurs
- N'utilisez PAS plt.savefig() - le graphique sera capturé automatiquement
- N'utilisez PAS plt.close() - le graphique doit rester ouvert pour être capturé
- TOUJOURS créer le graphique: plt.figure(figsize=(10, 6))
- Ensuite créer le graphique: plt.bar(), plt.plot(), plt.hist(), plt.scatter(), etc.
- TOUJOURS ajouter des étiquettes: plt.xlabel(), plt.ylabel(), plt.title()
- Le graphique sera automatiquement capturé après l'exécution de votre code
- Si l'utilisateur demande un "graphique" ou "diagramme", créez une visualisation appropriée basée sur les données

RÈGLES IMPORTANTES POUR LA SORTIE:
- TOUJOURS imprimer les résultats, statistiques et conclusions en utilisant des instructions print()
- Imprimer les infos DataFrame, statistiques, agrégations et toutes valeurs calculées
- Exemples:
  * print(f"Total: {df['column'].sum()}")
  * print(f"Moyenne: {df['column'].mean()}")
  * print(df.describe())
  * print(df.groupby('column').sum())
  * print(f"Top 5: {df.nlargest(5, 'column')}")

BIBLIOTHÈQUES DISPONIBLES:
- pandas (as pd)
- matplotlib.pyplot (as plt)
- json
- Fonctions Python standard: len, sum, max, min, etc.

DONNÉES DISPONIBLES:
- data_rows: liste de dictionnaires (les données réelles)
- data_columns: liste des noms de colonnes

Retournez UNIQUEMENT le code Python, pas d'explications ou de markdown. Le code sera exécuté directement."""
            
            # Build visualization instruction based on whether it's needed
            viz_instruction = ""
            if needs_visualization:
                viz_instruction = f"""

⚠️⚠️⚠️ VISUALIZATION REQUIRED - THIS IS MANDATORY ⚠️⚠️⚠️
The user's request contains visualization keywords: {[kw for kw in visualization_keywords if kw in query_lower]}.
YOU MUST CREATE A PLOT/CHART. DO NOT SKIP THIS STEP.

REQUIRED STEPS (DO ALL OF THESE):
1. Create a figure: plt.figure(figsize=(10, 6))
2. Choose appropriate plot type based on data:
   * plt.bar(x, y) for categorical comparisons (e.g., stations, vehicles, fuel types)
   * plt.plot(x, y) for trends over time
   * plt.hist(data, bins=20) for distributions
   * plt.scatter(x, y) for relationships
   * df.plot(kind='bar') or df.plot(kind='line') for DataFrame plots
3. ALWAYS add labels: 
   - plt.xlabel('Label')
   - plt.ylabel('Label')
   - plt.title('Title')
4. DO NOT use plt.show(), plt.close(), or plt.savefig() - the plot will be captured automatically
5. The plot MUST be created - if you're not sure what to plot, create a bar chart of the first column vs counts or a histogram of the first numeric column

EXAMPLE FOR BAR CHART:
plt.figure(figsize=(10, 6))
category_totals = df.groupby('category_column')['numeric_column'].sum()
plt.bar(range(len(category_totals)), category_totals.values)
plt.xticks(range(len(category_totals)), category_totals.index, rotation=45)
plt.xlabel('Category')
plt.ylabel('Total')
plt.title('Total by Category')
"""
            
            user_prompt = f"""DEMANDE D'ANALYSE DE L'UTILISATEUR: "{state['query']}"

INFORMATIONS SUR LES DONNÉES:
- Colonnes disponibles: {columns}
- Total de lignes: {len(rows)}
- Données d'échantillon (10 premières lignes):
{data_sample}

TÂCHE: Générez du code Python pour effectuer l'analyse demandée par l'utilisateur.

PREMIÈRE ÉTAPE CRITIQUE - VOUS DEVEZ FAIRE CECI:
1. TOUJOURS commencer votre code par: df = pd.DataFrame(data_rows)
   - Cela crée le DataFrame à partir de la variable data_rows
   - NE PAS sauter cette étape, même si vous pensez que c'est évident
   - NE PAS supposer que df existe déjà
   - Ceci DOIT être la première ligne de votre code
{viz_instruction}
INSTRUCTIONS ÉTAPE PAR ÉTAPE:
1. LA PREMIÈRE LIGNE DOIT ÊTRE: df = pd.DataFrame(data_rows)

2. Comprendre ce que l'utilisateur veut:
   - Lisez attentivement la demande de l'utilisateur
   - Identifiez quelle analyse il a besoin (statistiques, agrégations, comparaisons, visualisations, etc.)
   - Mappez la demande aux opérations pandas/matplotlib appropriées

3. Effectuer l'analyse:
   - Utilisez les méthodes pandas appropriées (groupby, agg, describe, value_counts, etc.)
   - Calculez les métriques demandées (somme, moyenne, comptage, pourcentage, etc.)
   - Si comparaison ou classement, utilisez le tri/filtrage approprié

4. Créer une visualisation si demandée:
   - Si l'utilisateur mentionne: "graphique", "diagramme", "tracer", "visualiser", "barre", "ligne", "histogramme", etc.
   - VOUS DEVEZ créer un graphique:
     * plt.figure(figsize=(10, 6))
     * Choisissez le type de graphique: plt.bar() pour catégories, plt.plot() pour tendances, plt.hist() pour distributions
     * Ajoutez des étiquettes: plt.xlabel(), plt.ylabel(), plt.title()
     * N'utilisez PAS plt.show(), plt.close(), ou plt.savefig()

5. Imprimer tous les résultats:
   - Imprimez les statistiques récapitulatives
   - Imprimez les agrégations
   - Imprimez les conclusions clés
   - Imprimez toutes les métriques calculées
   - Utilisez print() pour tout ce qui est important

EXEMPLES:

Exemple 1 - Statistiques:
df = pd.DataFrame(data_rows)
print("Statistiques récapitulatives:")
print(df.describe())
print(f"Total de lignes: {len(df)}")

Exemple 2 - Agrégation:
df = pd.DataFrame(data_rows)
result = df.groupby('category')['amount'].sum()
print("Total par catégorie:")
print(result)

Exemple 3 - Graphique en barres:
df = pd.DataFrame(data_rows)
category_totals = df.groupby('category')['amount'].sum()
plt.figure(figsize=(10, 6))
plt.bar(category_totals.index, category_totals.values)
plt.xlabel('Catégorie')
plt.ylabel('Montant total')
plt.title('Montant total par catégorie')
print("Totaux par catégorie:")
print(category_totals)

Exemple 4 - Top N:
df = pd.DataFrame(data_rows)
top_items = df.nlargest(5, 'value')
print("Top 5 éléments:")
print(top_items)

Maintenant générez le code pour la demande spécifique de l'utilisateur: "{state['query']}"
Rappelez-vous: Imprimez tous les résultats et créez une visualisation si demandée!"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            code = response.content.strip()
            logger.debug(f"Raw LLM response (first 500 chars): {code[:500]}")
            
            # Extract code from markdown blocks if present
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0].strip()
                logger.debug("Extracted code from ```python block")
            elif "```" in code:
                code = code.split("```")[1].split("```")[0].strip()
                logger.debug("Extracted code from ``` block")
            
            # Validate code is not empty
            if not code or len(code.strip()) == 0:
                logger.error("Generated code is empty")
                state["error"] = "Le code généré est vide. Veuillez reformuler votre demande."
                state["python_code"] = ""
                return state
            
            logger.debug(f"Code after extraction (first 300 chars): {code[:300]}")
            
            # CRITICAL: Ensure DataFrame is always created first
            # Check if code uses 'df' but doesn't create it
            try:
                # Check if DataFrame creation already exists (with various formats)
                has_df_creation = (
                    'df = pd.DataFrame(data_rows)' in code or
                    'df=pd.DataFrame(data_rows)' in code or
                    'df = pd.DataFrame(data_rows)' in code.replace(' ', '') or
                    'df=pd.DataFrame(data_rows)' in code.replace(' ', '')
                )
                
                # Check if code uses 'df' anywhere (more comprehensive check)
                code_lower = code.lower()
                # Check for any reference to 'df' that's not part of a string or comment
                # Look for patterns like: df[, df., df ), df], df\n, df,, df), len(df), etc.
                uses_df_patterns = [
                    r'\bdf\[', r'\bdf\.', r'\bdf\s', r'\bdf\n', r'\bdf,', r'\bdf\)', r'\bdf\]',
                    r'len\(df\)', r'print\(df\)', r'df\.', r'df\[', r'df\s', r'df,', r'df\)'
                ]
                uses_df = any(re.search(pattern, code_lower) for pattern in uses_df_patterns)
                
                # If code uses df but doesn't create it, ALWAYS prepend DataFrame creation
                if uses_df and not has_df_creation:
                    logger.info("Code uses 'df' but doesn't create it - prepending DataFrame creation")
                    code = "df = pd.DataFrame(data_rows)\n\n" + code
                    has_df_creation = True
                elif not has_df_creation and any(keyword in state['query'].lower() for keyword in ['chart', 'graph', 'plot', 'visualize', 'analyse', 'analyze', 'statistique', 'statistic']):
                    # Safety: if analysis/visualization is requested, always create DataFrame
                    logger.info("Analysis/visualization requested - prepending DataFrame creation for safety")
                    code = "df = pd.DataFrame(data_rows)\n\n" + code
                    has_df_creation = True
                
                # Ensure DataFrame creation is at the very beginning (move if needed)
                if has_df_creation:
                    lines = code.split('\n')
                    df_creation_idx = None
                    
                    for i, line in enumerate(lines):
                        line_lower = line.lower().strip()
                        # Skip comments and empty lines
                        if not line_lower or line_lower.startswith('#'):
                            continue
                        if 'df' in line_lower and ('pd.dataframe' in line_lower or 'pd.dataframe' in line_lower.replace(' ', '')):
                            df_creation_idx = i
                            break
                    
                    # If df creation exists but is not at the start, move it there
                    if df_creation_idx is not None and df_creation_idx > 0:
                        logger.info(f"Moving DataFrame creation from line {df_creation_idx} to beginning")
                        df_creation_line = lines.pop(df_creation_idx)
                        # Find first non-comment, non-empty line
                        insert_idx = 0
                        for i, line in enumerate(lines):
                            if line.strip() and not line.strip().startswith('#'):
                                insert_idx = i
                                break
                        lines.insert(insert_idx, df_creation_line)
                        code = '\n'.join(lines)
                
            except Exception as validation_error:
                logger.error(f"Error during code validation: {validation_error}", exc_info=True)
                # If validation fails, still try to add DataFrame creation as safety measure
                if 'df = pd.DataFrame(data_rows)' not in code:
                    logger.warning("Validation failed, adding DataFrame creation as fallback")
                    code = "df = pd.DataFrame(data_rows)\n\n" + code
            
            # If visualization is needed but code doesn't create a plot, inject plot code
            if needs_visualization:
                has_plot_code = any(plot_cmd in code.lower() for plot_cmd in ['plt.', 'matplotlib', 'plot(', 'bar(', 'hist(', 'scatter(', 'df.plot('])
                if not has_plot_code:
                    logger.warning("Visualization requested but code doesn't create plot - injecting plot code")
                    # Add plot code after DataFrame creation
                    plot_injection = """
# Create visualization as requested
plt.figure(figsize=(10, 6))
# Determine appropriate plot type based on data
numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

if len(numeric_cols) > 0 and len(categorical_cols) > 0:
    # Bar chart: categorical vs numeric
    cat_col = categorical_cols[0]
    num_col = numeric_cols[0]
    if len(df) <= 20:
        grouped = df.groupby(cat_col)[num_col].sum().head(10)
        plt.bar(range(len(grouped)), grouped.values)
        plt.xticks(range(len(grouped)), grouped.index, rotation=45, ha='right')
        plt.xlabel(cat_col)
        plt.ylabel(num_col)
        plt.title(f'{num_col} by {cat_col}')
    else:
        plt.hist(df[num_col].dropna(), bins=20)
        plt.xlabel(num_col)
        plt.ylabel('Frequency')
        plt.title(f'Distribution of {num_col}')
elif len(numeric_cols) > 0:
    # Histogram of first numeric column
    num_col = numeric_cols[0]
    plt.hist(df[num_col].dropna(), bins=20)
    plt.xlabel(num_col)
    plt.ylabel('Frequency')
    plt.title(f'Distribution of {num_col}')
elif len(categorical_cols) > 0:
    # Bar chart of value counts
    cat_col = categorical_cols[0]
    value_counts = df[cat_col].value_counts().head(10)
    plt.bar(range(len(value_counts)), value_counts.values)
    plt.xticks(range(len(value_counts)), value_counts.index, rotation=45, ha='right')
    plt.xlabel(cat_col)
    plt.ylabel('Count')
    plt.title(f'Count by {cat_col}')
"""
                    # Insert after DataFrame creation
                    if 'df = pd.DataFrame(data_rows)' in code:
                        code = code.replace('df = pd.DataFrame(data_rows)', f'df = pd.DataFrame(data_rows){plot_injection}')
                    else:
                        # Prepend if DataFrame creation wasn't found
                        code = f"df = pd.DataFrame(data_rows){plot_injection}\n\n{code}"
                    logger.info("Injected plot code into generated code")
            
            state["python_code"] = code
            logger.info(f"Generated Python code for analysis ({len(code)} chars)")
            # Log if visualization keywords are in the query
            if any(keyword in state['query'].lower() for keyword in ['chart', 'graph', 'plot', 'visualize', 'visualization', 'bar', 'line', 'histogram']):
                logger.info("Query contains visualization keywords - expecting a plot to be generated")
                # Check if generated code contains plot commands
                if any(plot_cmd in code.lower() for plot_cmd in ['plt.', 'matplotlib', 'plot(', 'bar(', 'hist(']):
                    logger.info("Generated code contains plot commands")
                else:
                    logger.warning("Query requests visualization but generated code doesn't contain plot commands")
            
        except Exception as e:
            logger.error(f"Error generating code: {e}", exc_info=True)
            # Try to recover by creating minimal valid code
            try:
                # If we have data, create a basic DataFrame and analysis
                if state.get("data") and state["data"].get("rows"):
                    logger.warning("Attempting to recover from code generation error with fallback code")
                    fallback_code = """df = pd.DataFrame(data_rows)
print(f"DataFrame created with {len(df)} rows and {len(df.columns)} columns")
print("\\nColumns:", df.columns.tolist())
print("\\nFirst few rows:")
print(df.head())
print("\\nSummary statistics:")
print(df.describe())"""
                    state["python_code"] = fallback_code
                    logger.info("Using fallback code for analysis")
                else:
                    state["error"] = f"Erreur lors de la génération du code: {str(e)}. Veuillez reformuler votre demande."
                    state["python_code"] = ""
            except Exception as recovery_error:
                logger.error(f"Error during recovery: {recovery_error}")
                state["error"] = f"Erreur lors de la génération du code: {str(e)}. Veuillez reformuler votre demande."
                state["python_code"] = ""
        
        return state
    
    def _execute_code(self, state: AnalyzerState) -> AnalyzerState:
        """Safely execute the generated Python code."""
        try:
            if state.get("error") or not state.get("python_code"):
                return state
            
            code = state["python_code"]
            data = state["data"]
            rows = data.get("rows", [])
            columns = data.get("columns", [])
            
            # Security: Only allow safe operations
            # Block dangerous imports and operations
            dangerous_patterns = [
                "__import__", "eval", "exec", "compile", "open", "file",
                "input", "raw_input", "exit", "quit", "sys.exit",
                "os.system", "subprocess", "shutil", "pickle", "marshal"
            ]
            
            for pattern in dangerous_patterns:
                if pattern in code:
                    raise ValueError(f"Unsafe operation detected: {pattern}")
            
            # Prepare execution environment
            # Serialize non-JSON types (date, datetime, Decimal, UUID, etc.) for pandas DataFrame
            # pandas can handle date objects, but converting to strings ensures consistency
            serialized_rows = serialize_for_json(rows)
            
            exec_globals = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "range": range,
                    "enumerate": enumerate,
                    "zip": zip,
                    "sum": sum,
                    "max": max,
                    "min": min,
                    "abs": abs,
                    "round": round,
                    "sorted": sorted,
                    "json": json,
                },
                "pd": pd,
                "plt": plt,
                "data_rows": serialized_rows,  # Use serialized rows with date strings
                "data_columns": columns,
                "DataFrame": pd.DataFrame,
            }
            
            exec_locals = {}
            
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            try:
                # Execute the code
                exec(code, exec_globals, exec_locals)
                logger.info("Code execution completed")
                
                # IMPORTANT: Check for matplotlib figures IMMEDIATELY after execution
                # before any cleanup happens
                try:
                    # Force matplotlib to create/register any pending figures
                    plt.ioff()  # Turn off interactive mode
                    
                    num_figures = plt.get_fignums()
                    logger.info(f"Checking for matplotlib figures: found {len(num_figures)} figure(s)")
                    
                    # Also check if any figures exist in the figure manager
                    import matplotlib._pylab_helpers
                    if hasattr(matplotlib._pylab_helpers, 'Gcf'):
                        all_figures = matplotlib._pylab_helpers.Gcf.get_all_fig_managers()
                        logger.info(f"Figure managers found: {len(all_figures)}")
                    
                    if num_figures:
                        logger.info(f"Found {len(num_figures)} matplotlib figure(s), converting to base64...")
                        
                        # Save plot directly to BytesIO buffer (in-memory, no file)
                        buffer = BytesIO()
                        # Save all figures to the buffer
                        for fig_num in num_figures:
                            try:
                                fig = plt.figure(fig_num)
                                if fig:
                                    fig.savefig(buffer, format='png', bbox_inches='tight', dpi=100, facecolor='white')
                                    logger.info(f"Saved figure {fig_num} to buffer")
                            except Exception as fig_error:
                                logger.warning(f"Error saving figure {fig_num}: {fig_error}")
                        
                        # Don't close figures yet - keep them for potential retry
                        # plt.close('all')
                        
                        # Convert to base64
                        buffer.seek(0)
                        plot_bytes = buffer.read()
                        buffer.close()
                        
                        if plot_bytes and len(plot_bytes) > 0:
                            plot_data = base64.b64encode(plot_bytes).decode('utf-8')
                            if plot_data:
                                state["visualization"] = plot_data
                                logger.info(f"Successfully converted plot to base64 ({len(plot_data)} chars, {len(plot_bytes)} bytes)")
                                # Now safe to close figures
                                plt.close('all')
                            else:
                                logger.warning("Plot data is empty after base64 encoding")
                                plt.close('all')
                        else:
                            logger.warning(f"Plot bytes are empty (length: {len(plot_bytes) if plot_bytes else 0})")
                            plt.close('all')
                    else:
                        logger.warning("No matplotlib figures found after code execution")
                        # Check if code contains plot commands but no figures were created
                        if any(plot_cmd in code.lower() for plot_cmd in ['plt.', 'matplotlib', 'plot(', 'bar(', 'hist(', 'scatter(']):
                            logger.warning("Code contains plot commands but no figures were created. This might indicate an error in plot generation.")
                        
                        # FALLBACK: If visualization was requested but no plot was created, try to create one
                        query_lower = state['query'].lower()
                        visualization_keywords = ['chart', 'graph', 'plot', 'visualize', 'visualization', 'bar', 'line', 'histogram', 'pie', 'scatter']
                        needs_visualization = any(keyword in query_lower for keyword in visualization_keywords)
                        
                        if needs_visualization and 'df' in exec_locals:
                            try:
                                df = exec_locals['df']
                                if isinstance(df, pd.DataFrame) and len(df) > 0:
                                    logger.info("Visualization requested but not created - generating fallback plot")
                                    plt.close('all')  # Clean up first
                                    
                                    # Create a simple plot based on the data
                                    fig, ax = plt.subplots(figsize=(10, 6))
                                    
                                    # Try to create an appropriate plot based on data structure
                                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                                    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                                    
                                    if len(numeric_cols) > 0 and len(categorical_cols) > 0:
                                        # Bar chart: categorical vs numeric
                                        cat_col = categorical_cols[0]
                                        num_col = numeric_cols[0]
                                        if len(df) <= 20:  # Only if reasonable number of categories
                                            grouped = df.groupby(cat_col)[num_col].sum().head(10)
                                            ax.bar(range(len(grouped)), grouped.values)
                                            ax.set_xticks(range(len(grouped)))
                                            ax.set_xticklabels(grouped.index, rotation=45, ha='right')
                                            ax.set_xlabel(cat_col)
                                            ax.set_ylabel(num_col)
                                            ax.set_title(f'{num_col} by {cat_col}')
                                        else:
                                            # Histogram of numeric column
                                            ax.hist(df[num_col].dropna(), bins=20)
                                            ax.set_xlabel(num_col)
                                            ax.set_ylabel('Frequency')
                                            ax.set_title(f'Distribution of {num_col}')
                                    elif len(numeric_cols) > 0:
                                        # Histogram of first numeric column
                                        num_col = numeric_cols[0]
                                        ax.hist(df[num_col].dropna(), bins=20)
                                        ax.set_xlabel(num_col)
                                        ax.set_ylabel('Frequency')
                                        ax.set_title(f'Distribution of {num_col}')
                                    elif len(categorical_cols) > 0:
                                        # Bar chart of value counts
                                        cat_col = categorical_cols[0]
                                        value_counts = df[cat_col].value_counts().head(10)
                                        ax.bar(range(len(value_counts)), value_counts.values)
                                        ax.set_xticks(range(len(value_counts)))
                                        ax.set_xticklabels(value_counts.index, rotation=45, ha='right')
                                        ax.set_xlabel(cat_col)
                                        ax.set_ylabel('Count')
                                        ax.set_title(f'Count by {cat_col}')
                                    else:
                                        # Default: simple bar chart of row counts
                                        ax.bar(['Total'], [len(df)])
                                        ax.set_ylabel('Count')
                                        ax.set_title('Data Summary')
                                    
                                    plt.tight_layout()
                                    
                                    # Save to buffer
                                    buffer = BytesIO()
                                    fig.savefig(buffer, format='png', bbox_inches='tight', dpi=100, facecolor='white')
                                    buffer.seek(0)
                                    plot_bytes = buffer.read()
                                    buffer.close()
                                    plt.close('all')
                                    
                                    if plot_bytes and len(plot_bytes) > 0:
                                        plot_data = base64.b64encode(plot_bytes).decode('utf-8')
                                        state["visualization"] = plot_data
                                        logger.info(f"Successfully created fallback plot ({len(plot_data)} chars)")
                                    else:
                                        logger.warning("Fallback plot creation failed - empty buffer")
                            except Exception as fallback_error:
                                logger.error(f"Error creating fallback plot: {fallback_error}", exc_info=True)
                        
                        plt.close('all')
                        # Also check if a plot file was created by the code
                        import os
                        plot_paths = ["/tmp/plot.png", "plot.png", "/app/plot.png", "./plot.png"]
                        for plot_path in plot_paths:
                            try:
                                if os.path.exists(plot_path):
                                    logger.info(f"Found plot file at {plot_path}, converting to base64...")
                                    with open(plot_path, 'rb') as f:
                                        plot_data = base64.b64encode(f.read()).decode('utf-8')
                                        if plot_data:
                                            state["visualization"] = plot_data
                                            logger.info(f"Loaded plot from file ({len(plot_data)} chars)")
                                    # Clean up
                                    os.remove(plot_path)
                                    break
                            except Exception as e:
                                logger.warning(f"Could not load plot from {plot_path}: {e}")
                except Exception as e:
                    logger.error(f"Error processing visualization: {e}", exc_info=True)
                
                # Get output
                output = captured_output.getvalue()
                
                # Also check for any variables that might have been printed or computed
                # If no stdout output, try to get DataFrame info or summary
                if not output.strip():
                    # Check if DataFrame was created
                    if 'df' in exec_locals:
                        df = exec_locals['df']
                        if isinstance(df, pd.DataFrame):
                            output = f"DataFrame created with {len(df)} rows and {len(df.columns)} columns.\n\n"
                            output += f"Shape: {df.shape}\n"
                            output += f"Columns: {', '.join(df.columns.tolist())}\n\n"
                            output += "First few rows:\n"
                            output += str(df.head().to_string())
                            output += "\n\nSummary statistics:\n"
                            output += str(df.describe().to_string())
                    elif 'result' in exec_locals:
                        output = str(exec_locals['result'])
                    else:
                        # Check for any DataFrames or results in locals
                        for var_name, var_value in exec_locals.items():
                            if isinstance(var_value, pd.DataFrame):
                                output += f"\n{var_name} DataFrame:\n"
                                output += f"Shape: {var_value.shape}\n"
                                output += f"Columns: {', '.join(var_value.columns.tolist())}\n"
                                output += f"\nFirst 5 rows:\n{var_value.head().to_string()}\n"
                                break
                
                # Always set execution_result, even if empty
                state["execution_result"] = output.strip() if output.strip() else "Code exécuté avec succès. Vérifiez la visualisation si générée."
                
            finally:
                sys.stdout = old_stdout
            
            logger.info("Code executed successfully")
            
        except Exception as e:
            logger.error(f"Error executing code: {e}")
            state["error"] = f"Erreur d'exécution du code: {str(e)}"
            state["execution_result"] = ""
        
        return state
    
    def _analyze_results(self, state: AnalyzerState) -> AnalyzerState:
        """Analyze the execution results and generate insights."""
        try:
            if state.get("error"):
                # If there's an error, still try to provide a helpful response
                error_msg = state.get("error", "Erreur inconnue")
                state["analysis"] = f"J'ai rencontré une erreur lors de l'analyse des données: {error_msg}. Veuillez vérifier votre requête et réessayer."
                state["insights"] = ["Erreur survenue pendant l'analyse"]
                return state
            
            execution_result = state.get("execution_result", "")
            code = state.get("python_code", "")
            has_visualization = bool(state.get("visualization"))
            original_query = state.get("query", "")
            
            # If execution result is empty or minimal, provide a helpful message
            if not execution_result or len(execution_result.strip()) < 10:
                state["analysis"] = "L'analyse est terminée, mais aucun résultat significatif n'a été généré. Veuillez vérifier si votre requête est suffisamment spécifique ou si les données contiennent les informations que vous recherchez."
                state["insights"] = ["Analyse terminée avec sortie minimale"]
                return state
            
            system_prompt = """Vous êtes un expert analyste de données pour la gestion de carburant Total Energies. Votre travail est d'interpréter les résultats de l'exécution de code Python sur les données de gestion de carburant et de fournir un résumé clair et complet.

Votre réponse doit:
1. Expliquer clairement quelle analyse a été effectuée (consommation de carburant, inventaire, transactions, etc.)
2. Mettre en évidence les conclusions et insights clés liés à la gestion de carburant
3. Présenter les statistiques ou métriques les plus importantes (quantités de carburant, coûts, efficacité, etc.)
4. Si une visualisation a été créée, décrire ce qu'elle montre dans le contexte de la gestion de carburant
5. Rendre l'analyse facile à comprendre pour les utilisateurs non techniques
6. Être concise mais complète
7. Répondre toujours en français

Écrivez dans un ton clair et professionnel. Utilisez la terminologie de gestion de carburant de manière appropriée."""
            
            user_prompt = f"""DEMANDE ORIGINALE DE L'UTILISATEUR: "{original_query}"

CODE PYTHON QUI A ÉTÉ EXÉCUTÉ:
```python
{code}
```

SORTIE/RÉSULTATS D'EXÉCUTION:
{execution_result}

VISUALISATION CRÉÉE: {'Oui - un graphique a été généré' if has_visualization else 'Non'}

TÂCHE: Fournir un résumé d'analyse complet qui:
1. Explique quelle analyse a été effectuée basée sur la demande de l'utilisateur
2. Met en évidence les principales conclusions de la sortie d'exécution
3. Présente les statistiques, métriques ou modèles importants découverts
4. Si une visualisation a été créée, décrit ce qu'elle montre et quels insights elle fournit
5. Rend les résultats faciles à comprendre

Écrivez un résumé clair et bien structuré qui répond directement à la demande originale de l'utilisateur: "{original_query}"

Concentrez-vous sur les insights actionnables et les conclusions clés. Répondez en français."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            state["analysis"] = response.content
            
            # Extract insights
            insights_prompt = f"""Extract 3-5 key insights from this analysis:
{state['analysis']}

Return as a JSON array of strings."""
            
            insights_messages = [
                SystemMessage(content="Extract key insights as a JSON array."),
                HumanMessage(content=insights_prompt)
            ]
            
            insights_response = self.llm.invoke(insights_messages)
            insights_content = insights_response.content.strip()
            
            # Parse insights
            try:
                if "```json" in insights_content:
                    insights_content = insights_content.split("```json")[1].split("```")[0].strip()
                elif "```" in insights_content:
                    insights_content = insights_content.split("```")[1].split("```")[0].strip()
                
                insights = json.loads(insights_content)
                if isinstance(insights, list):
                    state["insights"] = insights
                else:
                    state["insights"] = [insights] if insights else []
            except:
                # Fallback
                sentences = [s.strip() for s in state["analysis"].split('.') if s.strip()]
                state["insights"] = sentences[:5]
            
        except Exception as e:
            logger.error(f"Error analyzing results: {e}")
            state["error"] = str(e)
            if not state.get("analysis"):
                state["analysis"] = execution_result if execution_result else "Analyse terminée mais la génération du résumé a échoué."
        
        return state
    
    async def analyze(self, query: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze data based on the query."""
        initial_state: AnalyzerState = {
            "query": query,
            "sql_query": None,
            "data": data,
            "python_code": None,
            "execution_result": None,
            "visualization": None,
            "analysis": "",
            "insights": [],
            "error": None
        }
        
        try:
            result = await self.graph.ainvoke(initial_state)
            visualization = result.get("visualization")
            
            # Log visualization status
            if visualization:
                logger.info(f"Analyzer returning visualization ({len(visualization)} base64 chars)")
            else:
                logger.warning("Analyzer completed but no visualization found in result")
            
            return {
                "analysis": result.get("analysis", ""),
                "insights": result.get("insights", []),
                "python_code": result.get("python_code", ""),
                "execution_result": result.get("execution_result", ""),
                "visualization": visualization,  # Base64 encoded
                "sql_query": result.get("sql_query"),
                "error": result.get("error")
            }
        except Exception as e:
            logger.error(f"Error in analyzer agent: {e}")
            return {
                "analysis": "",
                "insights": [],
                "python_code": "",
                "execution_result": "",
                "visualization": None,
                "sql_query": None,
                "error": str(e)
            }


# Global instance - initialize only if API key is available
try:
    if settings.OPENAI_API_KEY:
        analyzer_agent = AnalyzerAgent()
    else:
        analyzer_agent = None
        logger.warning("Analyzer agent not initialized: OPENAI_API_KEY not set")
except Exception as e:
    analyzer_agent = None
    logger.error(f"Failed to initialize Analyzer agent: {e}")
