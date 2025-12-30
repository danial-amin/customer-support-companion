"""RAG (Retrieval Augmented Generation) agent using Pinecone."""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from app.config import settings
from app.services.pinecone_service import pinecone_service
from app.services.document_service import document_service
import logging

logger = logging.getLogger(__name__)


class RAGState(TypedDict):
    """State for RAG agent."""
    query: str
    context: List[str]
    answer: str
    error: Optional[str]


class RAGAgent:
    """RAG agent for answering questions using vector search."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
        self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow for RAG."""
        workflow = StateGraph(RAGState)
        
        workflow.add_node("retrieve", self._retrieve_context)
        workflow.add_node("generate", self._generate_answer)
        
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        return workflow.compile()
    
    def _retrieve_context(self, state: RAGState) -> RAGState:
        """Retrieve relevant context from Pinecone using hybrid search."""
        try:
            if not pinecone_service.is_available():
                state["error"] = "Pinecone service is not available"
                state["context"] = []
                return state
            
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(state["query"])
            
            # Extract keywords from query for hybrid search
            keywords = document_service.extract_keywords(state["query"])
            logger.info(f"Extracted keywords: {keywords[:10]}")
            
            # Use hybrid search (combines semantic + keyword matching)
            results = pinecone_service.hybrid_query(
                vector=query_embedding,
                keywords=keywords,
                top_k=5,
                keyword_weight=0.3  # 30% keyword, 70% semantic
            )
            
            # Extract context from results
            context = []
            for match in results:
                if match.get("metadata"):
                    text = match["metadata"].get("text", "")
                    source = match["metadata"].get("source", "unknown")
                    if text:
                        # Include source info in context
                        context.append(f"[Source: {source}]\n{text}")
            
            state["context"] = context
            logger.info(f"Retrieved {len(context)} context chunks using hybrid search")
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            state["error"] = str(e)
            state["context"] = []
        
        return state
    
    def _generate_answer(self, state: RAGState) -> RAGState:
        """Generate answer using LLM with retrieved context."""
        try:
            context_text = "\n\n".join(state.get("context", []))
            
            system_prompt = """You are a helpful customer support assistant. 
            Use the provided context to answer the user's question accurately.
            If the context doesn't contain enough information, say so.
            Be concise and helpful."""
            
            user_prompt = f"""Context:
{context_text}

Question: {state['query']}

Please provide a helpful answer based on the context above."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            state["answer"] = response.content
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            state["error"] = str(e)
            state["answer"] = "I apologize, but I encountered an error while generating the answer."
        
        return state
    
    async def query(self, query: str) -> Dict[str, Any]:
        """Process a query through the RAG agent."""
        initial_state: RAGState = {
            "query": query,
            "context": [],
            "answer": "",
            "error": None
        }
        
        try:
            result = await self.graph.ainvoke(initial_state)
            return {
                "answer": result.get("answer", ""),
                "context_sources": len(result.get("context", [])),
                "error": result.get("error")
            }
        except Exception as e:
            logger.error(f"Error in RAG agent: {e}")
            return {
                "answer": "",
                "context_sources": 0,
                "error": str(e)
            }


# Global instance - initialize only if API key is available
try:
    if settings.OPENAI_API_KEY:
        rag_agent = RAGAgent()
    else:
        rag_agent = None
        logger.warning("RAG agent not initialized: OPENAI_API_KEY not set")
except Exception as e:
    rag_agent = None
    logger.error(f"Failed to initialize RAG agent: {e}")

