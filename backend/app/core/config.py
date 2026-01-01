from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_NAME: str = "Fashion AI Discovery Commerce"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="API_HOST")
    PORT: int = Field(default=8000, env="API_PORT")
    
    # Security
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./fashion_ai.db", env="DATABASE_URL")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_SESSION_TTL: int = Field(default=3600, env="REDIS_SESSION_TTL")
    
    # OpenAI
    OPENAI_API_KEY: str = Field(default="sk-test-key", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo", env="OPENAI_MODEL")
    
    # Embedding
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-large", env="EMBEDDING_MODEL")
    EMBEDDING_DIMENSIONS: int = Field(default=1536, env="EMBEDDING_DIMENSIONS")
    
    # Vector Database
    VECTOR_DB_TYPE: str = Field(default="pinecone", env="VECTOR_DB_TYPE")
    PINECONE_API_KEY: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: Optional[str] = Field(default=None, env="PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: Optional[str] = Field(default="fashion-products", env="PINECONE_INDEX_NAME")
    WEAVIATE_URL: Optional[str] = Field(default="http://localhost:8080", env="WEAVIATE_URL")
    WEAVIATE_API_KEY: Optional[str] = Field(default=None, env="WEAVIATE_API_KEY")
    
    # CORS
    ALLOWED_HOSTS: List[str] = Field(default=["*"])
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="logs/app.log", env="LOG_FILE")
    
    # MMR Algorithm
    MMR_LAMBDA: float = Field(default=0.7, env="MMR_LAMBDA")
    EXPLORATION_RATIO: float = Field(default=0.7, env="EXPLORATION_RATIO")
    EXPLOITATION_RATIO: float = Field(default=0.3, env="EXPLOITATION_RATIO")
    
    # Recommendation
    MAX_RECOMMENDATIONS: int = Field(default=10, env="MAX_RECOMMENDATIONS")
    MIN_SIMILARITY_THRESHOLD: float = Field(default=0.3, env="MIN_SIMILARITY_THRESHOLD")
    MAX_SIMILARITY_THRESHOLD: float = Field(default=0.9, env="MAX_SIMILARITY_THRESHOLD")
    RECENT_HISTORY_LIMIT: int = Field(default=5, env="RECENT_HISTORY_LIMIT")
    
    # Intent Analysis
    INTENT_CONFIDENCE_THRESHOLD: float = Field(default=0.8, env="INTENT_CONFIDENCE_THRESHOLD")
    MAX_FOLLOW_UP_QUESTIONS: int = Field(default=2, env="MAX_FOLLOW_UP_QUESTIONS")
    
    # Response Generation
    RESPONSE_TEMPLATE_PATH: str = Field(default="ml/response_generator/templates", env="RESPONSE_TEMPLATE_PATH")
    MAX_RESPONSE_LENGTH: int = Field(default=1000, env="MAX_RESPONSE_LENGTH")
    USE_EMOJIS: bool = Field(default=True, env="USE_EMOJIS")
    
    # Performance
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")
    MAX_CONCURRENT_REQUESTS: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    
    # Feature Flags
    ENABLE_IMAGE_SEARCH: bool = Field(default=False, env="ENABLE_IMAGE_SEARCH")
    ENABLE_VOICE_INTERFACE: bool = Field(default=False, env="ENABLE_VOICE_INTERFACE")
    ENABLE_MULTIMODAL: bool = Field(default=False, env="ENABLE_MULTIMODAL")
    ENABLE_AB_TESTING: bool = Field(default=True, env="ENABLE_AB_TESTING")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()