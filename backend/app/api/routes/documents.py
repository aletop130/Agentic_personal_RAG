from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime
import uuid
import logging

from app.services.document_processor import document_processor
from app.services.chunking import chunking_service
from app.services.embedding_service import embedding_service
from app.core.qdrant_service import qdrant_service
from app.core.document_store import document_store
from app.models.schemas import DocumentResponse, DeleteResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    try:
        doc_id = str(uuid.uuid4())
        
        file_type = document_processor.get_file_type(file.filename)
        file_content = await file.read()
        
        document_processor.validate_file_size(len(file_content))
        
        text = document_processor.extract_text(file_content, file.filename, file_type)
        
        metadata = {
            "doc_id": doc_id,
            "filename": file.filename,
            "file_type": file_type,
            "uploaded_at": datetime.now().isoformat(),
            "file_size": len(file_content)
        }
        
        chunks = chunking_service.chunk_document(text, metadata)
        
        qdrant_points = await embedding_service.create_qdrant_points(doc_id, chunks)
        
        success = await qdrant_service.upsert_points(qdrant_points)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store document in vector database"
            )
        
        doc_data = {
            "id": doc_id,
            "filename": file.filename,
            "file_type": file_type,
            "file_size": len(file_content),
            "uploaded_at": metadata["uploaded_at"],
            "chunk_count": len(chunks),
            "status": "completed",
            "metadata": {
                "doc_id": doc_id,
                "file_type": file_type
            }
        }
        
        document_store.add_document(doc_data)
        
        logger.info(f"Document uploaded successfully: {file.filename} (ID: {doc_id})")
        
        return DocumentResponse(**doc_data)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("", response_model=List[DocumentResponse])
async def list_documents():
    try:
        docs = document_store.get_all_documents()
        return [DocumentResponse(**doc) for doc in docs]
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents"
        )


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str):
    try:
        doc_info = document_store.get_document(doc_id)
        
        if not doc_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        chunks = await qdrant_service.get_document_chunks(doc_id)
        doc_info["chunk_count"] = len(chunks)
        
        return DocumentResponse(**doc_info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {doc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document"
        )


@router.delete("/{doc_id}", response_model=DeleteResponse)
async def delete_document(doc_id: str):
    try:
        doc_info = document_store.get_document(doc_id)
        
        if not doc_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        success = await qdrant_service.delete_document(doc_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete document from vector database"
            )
        
        document_store.delete_document(doc_id)
        doc_filename = doc_info["filename"]
        
        logger.info(f"Document deleted successfully: {doc_filename} (ID: {doc_id})")
        
        return {
            "success": True,
            "message": f"Document '{doc_filename}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document: {str(e)}"
        )


@router.delete("/all", response_model=DeleteResponse)
async def delete_all_documents():
    try:
        docs = document_store.get_all_documents()
        doc_count = len(docs)
        
        for doc in docs:
            await qdrant_service.delete_document(doc["id"])
        
        document_store.delete_all_documents()
        
        logger.info(f"All documents deleted: {doc_count} documents removed")
        
        return {
            "success": True,
            "message": f"Successfully deleted {doc_count} documents"
        }
        
    except Exception as e:
        logger.error(f"Error deleting all documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete documents: {str(e)}"
        )
