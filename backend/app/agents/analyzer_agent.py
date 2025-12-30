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
import io
import sys
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import base64
from io import BytesIO

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
            
            # Use SQL agent to get data
            sql_result = await sql_agent.query(state["query"])
            
            if sql_result.get("error"):
                state["error"] = f"Failed to fetch data: {sql_result['error']}"
                return state
            
            if sql_result.get("result"):
                state["data"] = sql_result["result"]
                state["sql_query"] = sql_result.get("sql_query", "")
            else:
                state["error"] = "No data retrieved from SQL query"
            
        except Exception as e:
            logger.error(f"Error getting data: {e}")
            state["error"] = str(e)
        
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
            data_sample = json.dumps(rows[:10], indent=2)  # Sample for context
            
            system_prompt = """You are a data analysis expert. Generate Python code to analyze the provided data.
            The code should:
            1. Create a pandas DataFrame from the data: df = pd.DataFrame(data_rows)
            2. Perform statistical analysis, aggregations, or visualizations as requested
            3. ALWAYS use print() statements to show results, statistics, and findings
            4. If visualization is requested, create a matplotlib plot
            
            CRITICAL RULES FOR VISUALIZATIONS:
            - DO NOT use plt.show() - it will cause errors
            - DO NOT use plt.savefig() - the plot will be captured automatically
            - DO NOT use plt.close() - the plot needs to remain open to be captured
            - Just create the plot: plt.figure(), then plt.plot(), plt.bar(), plt.hist(), etc.
            - Add labels: plt.xlabel(), plt.ylabel(), plt.title()
            - The plot will be automatically captured after your code runs
            
            IMPORTANT:
            - ALWAYS print results, statistics, and findings using print() statements
            - Print DataFrame info, statistics, aggregations, and any computed values
            - Example: print(f"Total: {df['column'].sum()}"), print(df.describe()), etc.
            
            Return ONLY the Python code, no explanations. The code will be executed in an environment with:
            - pandas (as pd)
            - matplotlib.pyplot (as plt)
            - json
            - The data will be available as a list of dictionaries in a variable called 'data_rows'
            - The columns will be available as a list in 'data_columns'
            
            Print all important results and statistics."""
            
            user_prompt = f"""Data columns: {columns}
            Sample data (first 10 rows): {data_sample}
            Total rows: {len(rows)}
            
            Analysis request: {state['query']}
            
            Generate Python code to:
            1. Create a DataFrame: df = pd.DataFrame(data_rows)
            2. Perform the requested analysis
            3. Print all results, statistics, and findings using print() statements
            4. If the request mentions charts, graphs, or visualizations:
               - Create a new figure: plt.figure(figsize=(10, 6))
               - Create the plot: plt.plot(), plt.bar(), plt.hist(), plt.scatter(), etc.
               - Add labels: plt.xlabel('X Label'), plt.ylabel('Y Label'), plt.title('Title')
               - DO NOT use plt.show() or plt.close() - these will prevent the plot from being captured
               - DO NOT use plt.savefig() - the plot will be automatically captured
            5. Always print summary statistics, aggregations, and key findings
            
            Example for a bar chart:
            plt.figure(figsize=(10, 6))
            plt.bar(x_values, y_values)
            plt.xlabel('X Label')
            plt.ylabel('Y Label')
            plt.title('Chart Title')
            
            Make sure to use print() for all important outputs!"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            code = response.content.strip()
            
            # Extract code from markdown blocks if present
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].split("```")[0].strip()
            
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
            logger.error(f"Error generating code: {e}")
            state["error"] = str(e)
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
                "data_rows": rows,
                "data_columns": columns,
                "DataFrame": pd.DataFrame,
            }
            
            exec_locals = {}
            
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            try:
                # Execute the code
                exec(code, exec_globals, exec_locals)
                logger.info("Code execution completed")
                
                # IMPORTANT: Check for matplotlib figures IMMEDIATELY after execution
                # before any cleanup happens
                try:
                    num_figures = plt.get_fignums()
                    logger.info(f"Checking for matplotlib figures: found {len(num_figures)} figure(s)")
                    
                    if num_figures:
                        logger.info(f"Found {len(num_figures)} matplotlib figure(s), converting to base64...")
                        
                        # Save plot directly to BytesIO buffer (in-memory, no file)
                        buffer = BytesIO()
                        # Save all figures to the buffer
                        for fig_num in num_figures:
                            fig = plt.figure(fig_num)
                            fig.savefig(buffer, format='png', bbox_inches='tight', dpi=100, facecolor='white')
                        
                        plt.close('all')
                        
                        # Convert to base64
                        buffer.seek(0)
                        plot_bytes = buffer.read()
                        buffer.close()
                        
                        if plot_bytes:
                            plot_data = base64.b64encode(plot_bytes).decode('utf-8')
                            if plot_data:
                                state["visualization"] = plot_data
                                logger.info(f"Successfully converted plot to base64 ({len(plot_data)} chars, {len(plot_bytes)} bytes)")
                            else:
                                logger.warning("Plot data is empty after base64 encoding")
                        else:
                            logger.warning("Plot bytes are empty")
                    else:
                        logger.warning("No matplotlib figures found after code execution")
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
                return state
            
            execution_result = state.get("execution_result", "")
            code = state.get("python_code", "")
            has_visualization = bool(state.get("visualization"))
            
            system_prompt = """You are a data analyst. Analyze the results from Python code execution.
            Provide a clear summary of what was analyzed, key findings, and insights.
            If a visualization was created, mention what it shows."""
            
            user_prompt = f"""Analysis Request: {state['query']}
            
            Python Code Executed:
{code}

Execution Output:
{execution_result}

Visualization Created: {'Yes' if has_visualization else 'No'}

Provide a comprehensive analysis summary with key insights."""
            
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
