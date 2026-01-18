from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class QdrantService:
    def __init__(self):
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection_name = settings.qdrant_collection_name
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        try:
            collections = self.client.get_collections()
            existing_collections = [c.name for c in collections.collections]
            
            if self.collection_name not in existing_collections:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=4096,  # Adjust based on embedding model
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise
    
    async def upsert_points(self, points: List[PointStruct]) -> bool:
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Upserted {len(points)} points")
            return True
        except Exception as e:
            logger.error(f"Error upserting points: {e}")
            return False
    
    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.0,
        doc_id_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        try:
            filters = None
            if doc_id_filter:
                filters = Filter(
                    must=[
                        FieldCondition(
                            key="doc_id",
                            match=MatchValue(value=doc_id_filter)
                        )
                    ]
                )
            
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=filters,
                with_payload=True
            ).points
            
            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "doc_id": result.payload.get("doc_id"),
                    "chunk_index": result.payload.get("chunk_index"),
                    "text": result.payload.get("text"),
                    "metadata": result.payload.get("metadata", {})
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    async def delete_document(self, doc_id: str) -> bool:
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="doc_id",
                            match=MatchValue(value=doc_id)
                        )
                    ]
                )
            )
            logger.info(f"Deleted document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
    
    async def get_document_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        try:
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="doc_id",
                            match=MatchValue(value=doc_id)
                        )
                    ]
                ),
                limit=10000,
                with_payload=True
            )
            
            return [
                {
                    "id": point.id,
                    "chunk_index": point.payload.get("chunk_index"),
                    "text": point.payload.get("text"),
                    "metadata": point.payload.get("metadata", {})
                }
                for point in results[0]
            ]
        except Exception as e:
            logger.error(f"Error getting document chunks: {e}")
            return []


qdrant_service = QdrantService()
