from fastapi import APIRouter, HTTPException, status
import logging

from app.core.qdrant_service import qdrant_service
from app.core.regolo_service import regolo_service
from app.models.schemas import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check():
    qdrant_connected = False
    regolo_connected = False
    
    try:
        qdrant_service.client.get_collections()
        qdrant_connected = True
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
    
    try:
        await regolo_service.client.models.list()
        regolo_connected = True
    except Exception as e:
        logger.error(f"Regolo health check failed: {e}")
    
    overall_status = "healthy" if (qdrant_connected and regolo_connected) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        qdrant_connected=qdrant_connected,
        regolo_connected=regolo_connected
    )


@router.get("/qdrant")
async def qdrant_health():
    try:
        qdrant_service.client.get_collections()
        return {
            "status": "healthy",
            "service": "qdrant",
            "url": qdrant_service.client.get_cluster_info()
        }
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Qdrant service unavailable"
        )


@router.get("/regolo")
async def regolo_health():
    try:
        await regolo_service.client.models.list()
        return {
            "status": "healthy",
            "service": "regolo",
            "model": regolo_service.model
        }
    except Exception as e:
        logger.error(f"Regolo health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Regolo service unavailable"
        )
