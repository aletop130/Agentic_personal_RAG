from typing import TypedDict, Annotated, List, Dict, Any
import asyncio
import logging

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage

# App imports
from app.core.config import settings
from app.services.embedding_service import embedding_service
from app.core.qdrant_service import qdrant_service

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    retrieved_context: str
    sources: List[Dict[str, Any]]


@tool
def search_documents(query: str, top_k: int = 5) -> str:
    """Search for relevant documents based on the query.
    
    Args:
        query: The search query to find relevant document chunks
        top_k: Number of results to return (default: 5)
    
    Returns:
        Formatted context from retrieved documents with source citations.
    """
    logger.info(f"Searching documents with query: {query}, top_k: {top_k}")
    
    try:
        # Helper to run async code from this synchronous tool
        def run_async(coro):
            try:
                loop = asyncio.get_running_loop()
                return loop.run_until_complete(coro)
            except RuntimeError:
                # No running loop, create a new one
                return asyncio.run(coro)
        
        # 1. Generate Embedding
        query_embedding = run_async(embedding_service.generate_query_embedding(query))
        
        # 2. Search Qdrant
        results = run_async(qdrant_service.search(
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=0.3
        ))
        
        if not results:
            return "No relevant documents found."
        
        context_parts = []
        
        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            filename = metadata.get("filename", "Unknown")
            page = metadata.get("page_number", "N/A")
            score = result.get("score", 0.0)
            
            # Include source info in metadata format for extraction, but hide from LLM
            context_parts.append(
                f"<metadata_source_{i}>\n"
                f"filename:{filename}\n"
                f"page:{page}\n"
                f"score:{score:.2f}\n"
                f"</metadata_source_{i}>\n"
                f"{result['text']}"
            )
        
        return "\n---\n".join(context_parts)
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}", exc_info=True)
        return "I encountered an error while searching the documents."


def create_llm():
    """Create LLM instance compatible with Regolo AI."""
    return ChatOpenAI(
        model=settings.regolo_model,
        api_key=settings.regolo_api_key,
        base_url=settings.regolo_base_url,
        temperature=0.7,
        max_tokens=2048
    )


def create_rag_agent():
    """Create a simple RAG agent using LangGraph."""
    
    llm = create_llm()
    
    # Bind tools to LLM
    tools = [search_documents]
    llm_with_tools = llm.bind_tools(tools)
    
    # System prompt
    system_prompt = """Sei un assistente AI utile che risponde alle domande basandoti sui documenti caricati.

REGOLE:
- Usa il tool search_documents quando l'utente chiede informazioni che potrebbero essere nei documenti
- Rispondi in italiano
- Se il contesto non contiene informazioni sufficienti, dillo chiaramente
- NON menzionare le fonti nel testo della risposta
- Le fonti verranno visualizzate separatamente dall'interfaccia
- Sii conciso e preciso"""
    
    # Define nodes
    def llm_node(state: AgentState) -> dict:
        """LLM decides whether to call tools or respond directly."""
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    # Use LangGraph's built-in ToolNode
    tool_node = ToolNode(tools)
    
    def should_continue(state: AgentState) -> str:
        """Decide whether to call tools or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If the LLM made a tool call, route to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END
    
    # Build graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", llm_node)
    workflow.add_node("tools", tool_node)
    
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()