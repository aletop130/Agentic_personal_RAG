from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage
import logging

from app.agents import create_rag_agent, AgentState
from app.core.config import settings
from app.core.document_store import document_store

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.agent = create_rag_agent()
    
    async def process_query(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            if conversation_history is None:
                conversation_history = []
            
            doc_count = document_store.get_document_count()
            logger.info(f"Processing query: '{query}', documents in store: {doc_count}")
            
            # Check if no documents
            if doc_count == 0:
                return {
                    "message": "Non ho ancora documenti caricati. Carica dei documenti prima di farmi domande.",
                    "sources": []
                }
            
            # Convert conversation history to LangChain messages
            messages = []
            for msg in conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append({"role": "assistant", "content": msg["content"]})
            
            # Add current query
            messages.append(HumanMessage(content=query))
            
            # Run agent
            result = self.agent.invoke({
                "messages": messages,
                "retrieved_context": "",
                "sources": []
            })
            
            # Extract response
            messages = result["messages"]
            final_message = messages[-1]
            
            # Get the response content
            if hasattr(final_message, 'content'):
                response_text = final_message.content
            else:
                response_text = str(final_message)
            
            # Extract sources if any tool was called
            sources = []
            for msg in messages:
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        if tool_call.get("name") == "search_documents":
                            args = tool_call.get("args", {})
                            # Sources will be embedded in tool responses
                            pass
            
            # Extract sources from tool messages
            for msg in messages:
                if hasattr(msg, 'content') and "<metadata_source_" in str(msg.content):
                    content = str(msg.content)
                    import re
                    source_pattern = r'<metadata_source_(\d+)>\nfilename:([^\n]+)\npage:([^\n]+)\nscore:([\d.]+)'
                    matches = re.findall(source_pattern, content)

                    for source_id, filename, page, score in matches:
                        if not any(s["filename"] == filename.strip() and s["page"] == page.strip() for s in sources):
                            sources.append({
                                "filename": filename.strip(),
                                "page": page.strip(),
                                "score": float(score)
                            })
            
            return {
                "message": response_text,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error processing RAG query: {e}")
            logger.exception("Full traceback:")
            return {
                "message": f"Si è verificato un errore: {str(e)}",
                "sources": []
            }


rag_service = RAGService()
