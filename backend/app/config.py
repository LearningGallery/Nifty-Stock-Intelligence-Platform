"""
Application Configuration
Loads settings from environment variables
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = Field(default="dev", env="ENVIRONMENT")
    AWS_REGION: str = Field(default="ap-south-1", env="AWS_REGION")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Bedrock Configuration
    BEDROCK_MODEL_ID: str = Field(
        default="anthropic.claude-3-5-sonnet-20240620-v1:0",
        env="BEDROCK_MODEL_ID"
    )
    BEDROCK_EMBEDDING_MODEL: str = Field(
        default="amazon.titan-embed-text-v2:0",
        env="BEDROCK_EMBEDDING_MODEL"
    )
    BEDROCK_MAX_TOKENS: int = Field(default=4096, env="BEDROCK_MAX_TOKENS")
    BEDROCK_TEMPERATURE: float = Field(default=0.7, env="BEDROCK_TEMPERATURE")
    
    # OpenSearch Configuration
    OPENSEARCH_ENDPOINT: str = Field(..., env="OPENSEARCH_ENDPOINT")
    OPENSEARCH_INDEX: str = Field(default="stock-documents", env="OPENSEARCH_INDEX")
    OPENSEARCH_USERNAME: Optional[str] = Field(default=None, env="OPENSEARCH_USERNAME")
    OPENSEARCH_PASSWORD: Optional[str] = Field(default=None, env="OPENSEARCH_PASSWORD")
    
    # DynamoDB Configuration
    CHAT_SESSIONS_TABLE: str = Field(..., env="CHAT_SESSIONS_TABLE")
    CHAT_MESSAGES_TABLE: str = Field(..., env="CHAT_MESSAGES_TABLE")
    DOCUMENT_METADATA_TABLE: str = Field(..., env="DOCUMENT_METADATA_TABLE")
    STOCK_ANALYSIS_CACHE_TABLE: str = Field(..., env="STOCK_ANALYSIS_CACHE_TABLE")
    
    # Cognito Configuration
    COGNITO_USER_POOL_ID: str = Field(..., env="COGNITO_USER_POOL_ID")
    COGNITO_CLIENT_ID: str = Field(..., env="COGNITO_CLIENT_ID")
    COGNITO_REGION: str = Field(default="ap-south-1", env="COGNITO_REGION")
    
    # S3 Configuration
    DATA_LAKE_BUCKET: str = Field(..., env="DATA_LAKE_BUCKET")
    
    # Redis Configuration
    REDIS_ENDPOINT: str = Field(..., env="REDIS_ENDPOINT")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    CACHE_TTL_SECONDS: int = Field(default=300, env="CACHE_TTL_SECONDS")
    
    # API Keys Secret
    API_KEYS_SECRET_NAME: str = Field(..., env="API_KEYS_SECRET_NAME")
    
    # Application Configuration
    ENABLE_XRAY: bool = Field(default=True, env="ENABLE_XRAY")
    ENABLE_CORS: bool = Field(default=True, env="ENABLE_CORS")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        env="ALLOWED_ORIGINS"
    )
    
    # RAG Configuration
    RAG_TOP_K: int = Field(default=5, env="RAG_TOP_K")
    RAG_SIMILARITY_THRESHOLD: float = Field(default=0.7, env="RAG_SIMILARITY_THRESHOLD")
    CHUNK_SIZE: int = Field(default=512, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=50, env="CHUNK_OVERLAP")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_origins(cls, v):
        """Parse comma-separated origins"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = None
        case_sensitive = True


# Create settings instance
settings = Settings()
