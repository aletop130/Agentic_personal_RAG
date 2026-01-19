from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
import json
import logging
from app.services.rag_service import rag_service
from app.models.schemas import ChatRequest, ChatResponse
from app.core.regolo_service import regolo_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.info("="*80)
        logger.info("CHAT REQUEST RECEIVED")
        logger.info(f"Message: '{request.message}'")
        logger.info(f"Message length: {len(request.message)} characters")
        logger.info(f"Conversation history length: {len(request.conversation_history)}")
        logger.info(f"Top K: {request.top_k}")
        
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]
        
        logger.info(f"Converted conversation history: {conversation_history}")
        
        response = await rag_service.process_query(
            query=request.message,
            conversation_history=conversation_history,
            top_k=request.top_k
        )
        
        logger.info(f"Response message: '{response.get('message', '')}'")
        logger.info(f"Response sources count: {len(response.get('sources', []))}")
        logger.info("="*80)
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]
        
        messages = conversation_history + [{"role": "user", "content": request.message}]
        
        async def generate():
            try:
                response = await rag_service.process_query(
                    query=request.message,
                    conversation_history=conversation_history,
                    top_k=request.top_k
                )
                
                yield f"data: {json.dumps({'type': 'sources', 'data': response.get('sources', [])})}\n\n"
                
                if response.get("message"):
                    for chunk in response["message"]:
                        yield f"data: {json.dumps({'type': 'content', 'data': chunk})}\n\n"
                
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
            except Exception as e:
                logger.error(f"Error in stream: {e}")
                yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except Exception as e:
        logger.error(f"Error setting up chat stream: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting up stream: {str(e)}"
        )


@router.post("/search")
async def search_documents(request: ChatRequest):
    try:
        from app.services.embedding_service import embedding_service
        from app.core.qdrant_service import qdrant_service
        
        query_embedding = await embedding_service.generate_query_embedding(request.message)
        
        results = await qdrant_service.search(
            query_vector=query_embedding,
            limit=request.top_k or 5,
            score_threshold=0.5
        )
        
        return {
            "query": request.message,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documents: {str(e)}"
        )


@router.post("/clear-history")
async def clear_history():
    return {
        "success": True,
        "message": "Conversation history cleared"
    }
