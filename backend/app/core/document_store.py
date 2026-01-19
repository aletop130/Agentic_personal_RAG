import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class DocumentStore:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = "documents_store.db"
        
        self.db_path = str(db_path)
        self._init_db()
    
    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    uploaded_at TEXT NOT NULL,
                    chunk_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'completed',
                    metadata TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info(f"Document store initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing document store: {e}")
            raise
    
    def add_document(self, doc_data: Dict[str, Any]) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            metadata_json = json.dumps(doc_data.get("metadata", {}))
            
            cursor.execute("""
                INSERT INTO documents (id, filename, file_type, file_size, uploaded_at, chunk_count, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_data["id"],
                doc_data["filename"],
                doc_data["file_type"],
                doc_data["file_size"],
                doc_data["uploaded_at"],
                doc_data["chunk_count"],
                doc_data["status"],
                metadata_json
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Document added: {doc_data['filename']}")
            return True
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return False
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, filename, file_type, file_size, uploaded_at, chunk_count, status, metadata
                FROM documents
                ORDER BY uploaded_at DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            documents = []
            for row in rows:
                doc = {
                    "id": row[0],
                    "filename": row[1],
                    "file_type": row[2],
                    "file_size": row[3],
                    "uploaded_at": row[4],
                    "chunk_count": row[5],
                    "status": row[6],
                    "metadata": json.loads(row[7]) if row[7] else {}
                }
                documents.append(doc)
            
            return documents
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
            return []
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, filename, file_type, file_size, uploaded_at, chunk_count, status, metadata
                FROM documents
                WHERE id = ?
            """, (doc_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "id": row[0],
                    "filename": row[1],
                    "file_type": row[2],
                    "file_size": row[3],
                    "uploaded_at": row[4],
                    "chunk_count": row[5],
                    "status": row[6],
                    "metadata": json.loads(row[7]) if row[7] else {}
                }
            return None
        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")
            return None
    
    def delete_document(self, doc_id: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            
            conn.commit()
            conn.close()
            logger.info(f"Document deleted: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
    
    def delete_all_documents(self) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM documents")
            
            conn.commit()
            conn.close()
            logger.info("All documents deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting all documents: {e}")
            return False
    
    def update_chunk_count(self, doc_id: str, chunk_count: int) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE documents
                SET chunk_count = ?
                WHERE id = ?
            """, (chunk_count, doc_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating chunk count: {e}")
            return False
    
    def get_document_count(self) -> int:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM documents")
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0


document_store = DocumentStore()
