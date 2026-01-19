from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from pathlib import Path

from app.core.config import settings
from app.api.routes import documents, rag, health

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentic RAG API",
    description="Retrieval-Augmented Generation API with Regolo AI and Qdrant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(rag.router)
app.include_router(health.router)

frontend_path = Path(__file__).parent.parent.parent / "frontend"

if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="frontend")

@app.get("/")
async def root():
    return {
        "message": "Agentic RAG API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
        "frontend": "/static/index.html"
    }


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Agentic RAG API...")
    logger.info(f"Backend running on: {settings.backend_host}:{settings.backend_port}")
    logger.info(f"Qdrant URL: {settings.qdrant_url}")
    logger.info(f"Regolo Model: {settings.regolo_model}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Agentic RAG API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )
