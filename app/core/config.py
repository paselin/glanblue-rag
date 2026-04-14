"""
Core configuration settings for the Granblue RAG system.
"""
from functools import lru_cache
from typing import Optional, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "DEBUG"  # DEBUG for troubleshooting
    
    # LLM API Configuration
    openai_api_key: str = "dummy-key"  # ローカルLLMの場合は不要だがフォールバック用
    openai_api_base: str = "http://localhost:1234/v1"  # Ollama/LM Studio等
    openai_model: str = "gpt-4-turbo-preview"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000
    
    # Embeddings Configuration
    embedding_provider: str = "huggingface"  # "openai" or "huggingface"
    embedding_model: str = "intfloat/multilingual-e5-large"
    embedding_device: str = "cpu"  # "cpu" or "cuda"
    
    # OpenAI Embeddings (embedding_provider="openai"の場合)
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_api_key: Optional[str] = None
    openai_embedding_api_base: str = "https://api.openai.com/v1"
    
    # Vector Database
    chroma_persist_dir: str = "./data/vector_db"
    collection_name: str = "granblue_knowledge"
    
    # Redis Cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_enabled: bool = False
    
    # Database
    database_url: str = "sqlite:///./data/app.db"
    
    # Scraping
    scraper_user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    scraper_delay: int = 2
    scraper_timeout: int = 30000
    
    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_top_k: int = 5
    
    # Rate Limiting
    rate_limit_per_hour: int = 100
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
