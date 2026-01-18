from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    regolo_api_key: str
    regolo_base_url: str = "https://api.regolo.ai/v1"
    regolo_model: str = "gpt-oss-120b"
    regolo_embedding_model: str = "qwen3-embedding-8b"

    qdrant_url: str = "http://localhost:7333"
    qdrant_collection_name: str = "documents"

    backend_port: int = 8000
    backend_host: str = "0.0.0.0"
    _cors_origins: str = "http://localhost:8000,http://127.0.0.1:8000,http://localhost:5173,http://localhost:3000,http://localhost:5500"

    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "./uploads"

    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5

    google_credentials_path: str = ""
    google_api_key: str = ""

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self._cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
