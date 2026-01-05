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
                error_msg = sql_result.get("error", "Unknown error")
                # Check if the error indicates the SQL agent couldn't generate a query
                if "Could not generate a valid SQL query" in error_msg or "not capable" in error_msg.lower():
                    state["error"] = f"Cannot analyze this request: {error_msg}. Please rephrase your query to ask for data that can be retrieved from the database."
                else:
                    state["error"] = f"Failed to fetch data for analysis: {error_msg}. Please ensure your query references valid database tables and columns."
                logger.warning(f"SQL agent failed: {error_msg}")
                return state
            
            # Validate that we got a proper SQL query
            sql_query = sql_result.get("sql_query", "")
            if not sql_query or not sql_query.upper().startswith("SELECT"):
                state["error"] = "The SQL agent did not generate a valid SQL query. Please rephrase your request to ask for data from the database."
                logger.warning(f"Invalid SQL query from SQL agent: {sql_query[:100]}")
                return state
            
            if sql_result.get("result"):
                data = sql_result["result"]
                rows = data.get("rows", [])
                if not rows or len(rows) == 0:
                    state["error"] = "No data found to analyze. The query returned empty results."
                    return state
                state["data"] = data
                state["sql_query"] = sql_query
                logger.info(f"Retrieved {len(rows)} rows for analysis")
            else:
                state["error"] = "No data retrieved from SQL query. Please check your query and try again."
            
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
                state["error"] = "No data rows to analyze"
                return state
            
            # Convert to DataFrame format for code generation
            # Serialize non-JSON types (date, datetime, Decimal, UUID, etc.) to strings
            serialized_rows = serialize_for_json(rows[:10])
            data_sample = json.dumps(serialized_rows, indent=2)  # Sample for context
            
            # Check if visualization is requested
            query_lower = state['query'].lower()
            visualization_keywords = ['chart', 'graph', 'plot', 'visualize', 'visualization', 'bar', 'line', 'histogram', 'pie', 'scatter']
            needs_visualization = any(keyword in query_lower for keyword in visualization_keywords)
            
            system_prompt = """You are an expert fuel management data analyst for Total Energies. Your job is to understand the user's analysis request for fuel management data and generate Python code to perform that analysis.

UNDERSTANDING THE REQUEST:
- Carefully read the user's query to understand what analysis they want for fuel management data
- Common analysis types for fuel management:
  * Statistical summaries: "show statistics", "describe the data", "summary" (for fuel transactions, consumption, inventory)
  * Aggregations: "total", "average", "count", "sum", "group by" (fuel consumption, costs, transactions by station/vehicle)
  * Comparisons: "compare", "difference", "which is higher" (fuel costs, consumption between stations/vehicles/departments)
  * Trends: "over time", "by month", "trend" (fuel consumption trends, price trends, transaction volume)
  * Distributions: "distribution", "histogram", "frequency" (fuel inventory levels, transaction amounts)
  * Visualizations: "chart", "graph", "plot", "visualize", "bar chart", "line chart" (fuel consumption charts, station performance)
  * Rankings: "top", "bottom", "highest", "lowest", "best", "worst" (top fuel stations, most fuel-efficient vehicles)
  * Calculations: "percentage", "ratio", "growth", "change" (fuel efficiency, cost per kilometer, inventory utilization)

CODE REQUIREMENTS:
1. ALWAYS start by creating a DataFrame: df = pd.DataFrame(data_rows)
2. Understand the data structure - check columns and data types
3. Perform the requested analysis
4. ALWAYS use print() statements to show ALL results, statistics, and findings
5. **IF THE USER ASKS FOR A CHART, GRAPH, OR PLOT, YOU MUST CREATE ONE**

CRITICAL RULES FOR VISUALIZATIONS:
- When visualization is requested, you MUST create a matplotlib plot
- DO NOT use plt.show() - it will cause errors
- DO NOT use plt.savefig() - the plot will be captured automatically
- DO NOT use plt.close() - the plot needs to remain open to be captured
- ALWAYS create the plot: plt.figure(figsize=(10, 6))
- Then create the plot: plt.bar(), plt.plot(), plt.hist(), plt.scatter(), etc.
- ALWAYS add labels: plt.xlabel(), plt.ylabel(), plt.title()
- The plot will be automatically captured after your code runs
- If user asks for "graph" or "chart", create an appropriate visualization based on the data

IMPORTANT OUTPUT RULES:
- ALWAYS print results, statistics, and findings using print() statements
- Print DataFrame info, statistics, aggregations, and any computed values
- Examples:
  * print(f"Total: {df['column'].sum()}")
  * print(f"Average: {df['column'].mean()}")
  * print(df.describe())
  * print(df.groupby('column').sum())
  * print(f"Top 5: {df.nlargest(5, 'column')}")

AVAILABLE LIBRARIES:
- pandas (as pd)
- matplotlib.pyplot (as plt)
- json
- Standard Python functions: len, sum, max, min, etc.

DATA AVAILABLE:
- data_rows: list of dictionaries (the actual data)
- data_columns: list of column names

Return ONLY the Python code, no explanations or markdown. The code will be executed directly."""
            
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
            
            user_prompt = f"""USER'S ANALYSIS REQUEST: "{state['query']}"

DATA INFORMATION:
- Columns available: {columns}
- Total rows: {len(rows)}
- Sample data (first 10 rows):
{data_sample}

TASK: Generate Python code to perform the analysis requested by the user.

CRITICAL FIRST STEP - YOU MUST DO THIS:
1. ALWAYS start your code with: df = pd.DataFrame(data_rows)
   - This creates the DataFrame from the data_rows variable
   - DO NOT skip this step, even if you think it's obvious
   - DO NOT assume df already exists
   - This MUST be the first line of your code
{viz_instruction}
STEP-BY-STEP INSTRUCTIONS:
1. FIRST LINE MUST BE: df = pd.DataFrame(data_rows)

2. Understand what the user wants:
   - Read the user's request carefully
   - Identify what analysis they need (statistics, aggregations, comparisons, visualizations, etc.)
   - Map the request to appropriate pandas/matplotlib operations

3. Perform the analysis:
   - Use appropriate pandas methods (groupby, agg, describe, value_counts, etc.)
   - Calculate requested metrics (sum, mean, count, percentage, etc.)
   - If comparing or ranking, use appropriate sorting/filtering

4. Create visualization if requested:
   - If user mentions: "chart", "graph", "plot", "visualize", "bar", "line", "histogram", etc.
   - YOU MUST create a plot:
     * plt.figure(figsize=(10, 6))
     * Choose plot type: plt.bar() for categories, plt.plot() for trends, plt.hist() for distributions
     * Add labels: plt.xlabel(), plt.ylabel(), plt.title()
     * DO NOT use plt.show(), plt.close(), or plt.savefig()

5. Print all results:
   - Print summary statistics
   - Print aggregations
   - Print key findings
   - Print any calculated metrics
   - Use print() for everything important

EXAMPLES:

Example 1 - Statistics:
df = pd.DataFrame(data_rows)
print("Summary Statistics:")
print(df.describe())
print(f"Total rows: {len(df)}")

Example 2 - Aggregation:
df = pd.DataFrame(data_rows)
result = df.groupby('category')['amount'].sum()
print("Total by category:")
print(result)

Example 3 - Bar Chart:
df = pd.DataFrame(data_rows)
category_totals = df.groupby('category')['amount'].sum()
plt.figure(figsize=(10, 6))
plt.bar(category_totals.index, category_totals.values)
plt.xlabel('Category')
plt.ylabel('Total Amount')
plt.title('Total Amount by Category')
print("Category totals:")
print(category_totals)

Example 4 - Top N:
df = pd.DataFrame(data_rows)
top_items = df.nlargest(5, 'value')
print("Top 5 items:")
print(top_items)

Now generate the code for the user's specific request: "{state['query']}"
Remember: Print all results and create visualization if requested!"""
            
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
                state["error"] = "Generated code is empty. Please try rephrasing your request."
                state["python_code"] = ""
                return state
            
            logger.debug(f"Code after extraction (first 300 chars): {code[:300]}")
            
            # CRITICAL: Ensure DataFrame is always created first
            # Check if code uses 'df' but doesn't create it
            try:
                # Always prepend DataFrame creation as a safety measure
                # This ensures df is always available regardless of what the LLM generates
                if 'df = pd.DataFrame(data_rows)' not in code and 'df=pd.DataFrame(data_rows)' not in code:
                    # Check if code actually uses df
                    code_lower = code.lower()
                    # Simple check: does code reference df in a way that suggests usage?
                    uses_df_indicators = ['df[', 'df.', 'df ', 'df\n', 'df,', 'df)', 'df]']
                    uses_df = any(indicator in code_lower for indicator in uses_df_indicators)
                    
                    if uses_df:
                        logger.info("Code uses 'df' - prepending DataFrame creation")
                        code = "df = pd.DataFrame(data_rows)\n\n" + code
                    else:
                        # Even if not explicitly used, add it for safety if code looks like it might need it
                        # (e.g., if it's a visualization request)
                        if any(keyword in state['query'].lower() for keyword in ['chart', 'graph', 'plot', 'visualize']):
                            logger.info("Visualization requested - prepending DataFrame creation for safety")
                            code = "df = pd.DataFrame(data_rows)\n\n" + code
                
                # Ensure DataFrame creation is at the very beginning (move if needed)
                lines = code.split('\n')
                df_creation_idx = None
                
                for i, line in enumerate(lines):
                    line_lower = line.lower().strip()
                    # Skip comments and empty lines
                    if not line_lower or line_lower.startswith('#'):
                        continue
                    if 'df' in line_lower and ('pd.dataframe' in line_lower or 'pd.DataFrame' in line_lower):
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
                    state["error"] = f"Error generating code: {str(e)}. Please try rephrasing your request."
                    state["python_code"] = ""
            except Exception as recovery_error:
                logger.error(f"Error during recovery: {recovery_error}")
                state["error"] = f"Error generating code: {str(e)}. Please try rephrasing your request."
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
                state["execution_result"] = output.strip() if output.strip() else "Code executed successfully. Check visualization if generated."
                
            finally:
                sys.stdout = old_stdout
            
            logger.info("Code executed successfully")
            
        except Exception as e:
            logger.error(f"Error executing code: {e}")
            state["error"] = f"Code execution error: {str(e)}"
            state["execution_result"] = ""
        
        return state
    
    def _analyze_results(self, state: AnalyzerState) -> AnalyzerState:
        """Analyze the execution results and generate insights."""
        try:
            if state.get("error"):
                # If there's an error, still try to provide a helpful response
                error_msg = state.get("error", "Unknown error")
                state["analysis"] = f"I encountered an error while analyzing the data: {error_msg}. Please check your query and try again."
                state["insights"] = ["Error occurred during analysis"]
                return state
            
            execution_result = state.get("execution_result", "")
            code = state.get("python_code", "")
            has_visualization = bool(state.get("visualization"))
            original_query = state.get("query", "")
            
            # If execution result is empty or minimal, provide a helpful message
            if not execution_result or len(execution_result.strip()) < 10:
                state["analysis"] = "The analysis completed, but no significant results were generated. Please check if your query is specific enough or if the data contains the information you're looking for."
                state["insights"] = ["Analysis completed with minimal output"]
                return state
            
            system_prompt = """You are an expert fuel management data analyst for Total Energies. Your job is to interpret the results from Python code execution on fuel management data and provide a clear, comprehensive summary.

Your response should:
1. Clearly explain what analysis was performed (fuel consumption, inventory, transactions, etc.)
2. Highlight the key findings and insights related to fuel management
3. Present the most important statistics or metrics (fuel quantities, costs, efficiency, etc.)
4. If a visualization was created, describe what it shows in the context of fuel management
5. Make the analysis easy to understand for non-technical users
6. Be concise but comprehensive
7. Always respond in the same language as the user's question (English or French)

Write in a clear, professional tone. Use fuel management terminology appropriately."""
            
            # Detect language from query
            query_lower = original_query.lower()
            is_french = any(word in query_lower for word in ['comment', 'quoi', 'où', 'quand', 'pourquoi', 'combien', 'quel', 'quelle', 'quelles', 'quels', 'analyse', 'montre', 'graphique', 'tendance'])
            
            if is_french:
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
            else:
            user_prompt = f"""ORIGINAL USER REQUEST: "{original_query}"

PYTHON CODE THAT WAS EXECUTED:
```python
{code}
```

EXECUTION OUTPUT/RESULTS:
{execution_result}

VISUALIZATION CREATED: {'Yes - a chart/graph was generated' if has_visualization else 'No'}

TASK: Provide a comprehensive analysis summary that:
1. Explains what analysis was performed based on the user's request
2. Highlights the key findings from the execution output
3. Presents important statistics, metrics, or patterns discovered
4. If a visualization was created, describe what it shows and what insights it provides
5. Makes the results easy to understand

Write a clear, well-structured summary that directly addresses the user's original request: "{original_query}"

Focus on actionable insights and key findings. Respond in the same language as the question."""
            
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
                state["analysis"] = execution_result if execution_result else "Analysis completed but summary generation failed."
        
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
