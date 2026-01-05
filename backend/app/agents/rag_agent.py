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
    sources: List[Dict[str, Any]]  # Store full source information
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
        # Use text-embedding-ada-002 which produces 1536-dimensional embeddings
        # This must match the Pinecone index dimension
        self.embeddings = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            model="text-embedding-ada-002"  # Explicitly set to ensure 1536 dimensions
        )
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
            sources = []
            seen_sources = set()  # Track unique sources
            
            if results:
                for match in results:
                    if match.get("metadata"):
                        metadata = match["metadata"]
                        text = metadata.get("text", "")
                        source = metadata.get("source", "unknown")
                        file_name = metadata.get("file_name", source)
                        file_type = metadata.get("file_type", "")
                        url = metadata.get("url", "")  # For SharePoint documents
                        chunk_index = metadata.get("chunk_index", 0)
                        total_chunks = metadata.get("total_chunks", 1)
                        score = match.get("score", 0.0)
                        
                        if text:
                            # Include source info in context for LLM
                            context.append(f"[Source: {source}]\n{text}")
                            
                            # Store full source information
                            source_info = {
                                "source": source,
                                "file_name": file_name,
                                "file_type": file_type,
                                "url": url,
                                "chunk_index": chunk_index,
                                "total_chunks": total_chunks,
                                "score": score,
                                "text_preview": text[:200] + "..." if len(text) > 200 else text
                            }
                            
                            # Add unique sources (by source name)
                            source_key = f"{source}_{file_name}"
                            if source_key not in seen_sources:
                                sources.append(source_info)
                                seen_sources.add(source_key)
            
            state["context"] = context
            state["sources"] = sources
            logger.info(f"Retrieved {len(context)} context chunks from {len(sources)} unique sources")
            
            # If no context found, log a warning
            if not context:
                logger.warning(f"No context found for query: {state['query']}. The index may be empty or the query doesn't match any documents.")
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            state["error"] = str(e)
            state["context"] = []
        
        return state
    
    def _generate_answer(self, state: RAGState) -> RAGState:
        """Generate answer using LLM with retrieved context."""
        try:
            context_list = state.get("context", [])
            context_text = "\n\n".join(context_list) if context_list else ""
            
            # If no context was found, provide helpful message
            if not context_text:
                # Detect language from query
                query_lower = state["query"].lower()
                is_french = any(word in query_lower for word in ['comment', 'quoi', 'où', 'quand', 'pourquoi', 'combien', 'quel', 'quelle', 'quelles', 'quels'])
                
                if is_french:
                    state["answer"] = (
                        "Je n'ai aucun document dans ma base de connaissances pour répondre à cette question. "
                        "Veuillez télécharger des documents pertinents en utilisant la page Documents, ou essayez de poser une question différente. "
                        "Si vous pensez que ces informations devraient être disponibles, les documents peuvent devoir être retéléchargés."
                    )
                else:
                    state["answer"] = (
                    "I don't have any documents in my knowledge base to answer that question. "
                    "Please upload relevant documents using the Documents page, or try asking a different question. "
                    "If you believe this information should be available, the documents may need to be re-uploaded after fixing the Pinecone index dimension."
                )
                return state
            
            system_prompt = """You are a helpful fuel management support assistant for Total Energies. 
            You help customers and staff with questions about fuel stations, fuel types, fuel cards, vehicles, 
            fuel transactions, inventory management, and fuel management policies.
            Use the provided context to answer the user's question accurately.
            If the context doesn't contain enough information, say so.
            Be concise and helpful. Always respond in the same language as the user's question."""
            
            # Detect language from query
            query_lower = state["query"].lower()
            is_french = any(word in query_lower for word in ['comment', 'quoi', 'où', 'quand', 'pourquoi', 'combien', 'quel', 'quelle', 'quelles', 'quels', 'explique', 'parle'])
            
            if is_french:
                user_prompt = f"""Contexte:
{context_text}

Question: {state['query']}

Veuillez fournir une réponse utile basée sur le contexte ci-dessus. Répondez en français."""
            else:
                user_prompt = f"""Context:
{context_text}

Question: {state['query']}

Please provide a helpful answer based on the context above. Respond in the same language as the question."""
            
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
            "sources": [],
            "answer": "",
            "error": None
        }
        
        try:
            result = await self.graph.ainvoke(initial_state)
            return {
                "answer": result.get("answer", ""),
                "context_sources": len(result.get("context", [])),
                "sources": result.get("sources", []),  # Return full source information
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

