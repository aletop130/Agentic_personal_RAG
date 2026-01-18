from typing import List, Dict, Any
from qdrant_client.models import PointStruct
from app.core.regolo_service import regolo_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.embedding_model = settings.regolo_embedding_model
    
    async def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 10
    ) -> List[List[float]]:
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                batch_embeddings = await self._generate_batch_embeddings(batch)
                embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i//batch_size}: {e}")
                raise
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings
    
    async def _generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        
        for text in texts:
            try:
                embedding = await regolo_service.generate_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Error generating embedding for text: {e}")
                raise
        
        return embeddings
    
    async def create_qdrant_points(
        self,
        doc_id: str,
        chunks: List[Dict[str, Any]]
    ) -> List[PointStruct]:
        import uuid
        texts = [chunk["text"] for chunk in chunks]
        embeddings = await self.generate_embeddings(texts)
        
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": chunk["text"],
                    "doc_id": doc_id,
                    "chunk_index": chunk["metadata"].get("chunk_index", i),
                    "metadata": chunk["metadata"]
                }
            )
            points.append(point)
        
        logger.info(f"Created {len(points)} Qdrant points")
        return points
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        try:
            embedding = await regolo_service.generate_embedding(query)
            return embedding
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise


embedding_service = EmbeddingService()
