from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ChunkingService:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_document(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        try:
            chunks = self.splitter.split_text(text)
            
            chunked_documents = []
            
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_index": i,
                    "chunk_size": len(chunk),
                    "total_chunks": len(chunks)
                })
                
                chunked_documents.append({
                    "text": chunk,
                    "metadata": chunk_metadata
                })
            
            logger.info(f"Chunked document into {len(chunks)} chunks")
            return chunked_documents
            
        except Exception as e:
            logger.error(f"Error chunking document: {e}")
            raise
    
    def chunk_with_page_numbers(
        self,
        pages: List[tuple],
        doc_id: str,
        filename: str
    ) -> List[Dict[str, Any]]:
        try:
            chunked_documents = []
            global_chunk_index = 0
            
            for page_num, page_text in pages:
                if not page_text.strip():
                    continue
                
                chunks = self.splitter.split_text(page_text)
                
                for chunk in chunks:
                    chunked_documents.append({
                        "text": chunk,
                        "metadata": {
                            "doc_id": doc_id,
                            "filename": filename,
                            "page_number": page_num,
                            "chunk_index": global_chunk_index,
                            "chunk_size": len(chunk)
                        }
                    })
                    global_chunk_index += 1
            
            logger.info(f"Chunked document into {len(chunked_documents)} chunks")
            return chunked_documents
            
        except Exception as e:
            logger.error(f"Error chunking document with page numbers: {e}")
            raise


chunking_service = ChunkingService()
