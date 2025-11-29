from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


from pathlib import Path

class Settings(BaseSettings):
    # Resolve .env path relative to this file to support running from root or backend dir
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8", extra="ignore")
    
    # Azure AI Foundry Agent Service
    AZURE_AI_PROJECT_CONNECTION_STRING: str = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING", "")
    AZURE_AI_PROJECT_ENDPOINT: str = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "https://your-ai-foundry.services.ai.azure.com/api/projects/your-project")
    AZURE_AI_PROJECT_NAME: str = os.getenv("AZURE_AI_PROJECT_NAME", "service-desk-agents")
    
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "https://your-openai.openai.azure.com/")
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_GPT4O_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT", "gpt-4o")
    AZURE_OPENAI_O1_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_O1_DEPLOYMENT", "o1-preview")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
    
    # Azure AI Search
    AZURE_SEARCH_ENDPOINT: str = os.getenv("AZURE_SEARCH_ENDPOINT", "https://your-search.search.windows.net")
    AZURE_SEARCH_KEY: Optional[str] = os.getenv("AZURE_SEARCH_KEY")
    AZURE_SEARCH_INDEX_NAME: str = os.getenv("AZURE_SEARCH_INDEX_NAME", "knowledge-base")
    
    # Azure Content Safety
    AZURE_CONTENT_SAFETY_ENDPOINT: str = os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT", "https://your-content-safety.cognitiveservices.azure.com/")
    AZURE_CONTENT_SAFETY_KEY: Optional[str] = os.getenv("AZURE_CONTENT_SAFETY_KEY")
    
    # Azure Cosmos DB
    AZURE_COSMOS_ENDPOINT: str = os.getenv("AZURE_COSMOS_ENDPOINT", "https://your-cosmos.documents.azure.com:443/")
    AZURE_COSMOS_KEY: Optional[str] = os.getenv("AZURE_COSMOS_KEY")
    AZURE_COSMOS_DATABASE_NAME: str = os.getenv("AZURE_COSMOS_DATABASE_NAME", "servicedesk")
    
    # Azure SQL Database
    AZURE_SQL_CONNECTION_STRING: Optional[str] = os.getenv("AZURE_SQL_CONNECTION_STRING")
    
    # Azure Cache for Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "your-redis.redis.cache.windows.net")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6380"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_SSL: bool = os.getenv("REDIS_SSL", "true").lower() == "true"
    
    # Azure Service Bus
    SERVICE_BUS_CONNECTION_STRING: Optional[str] = os.getenv("SERVICE_BUS_CONNECTION_STRING")
    SERVICE_BUS_QUEUE_NAME: str = os.getenv("SERVICE_BUS_QUEUE_NAME", "ticket-queue")
    
    # Azure Event Grid
    EVENT_GRID_ENDPOINT: Optional[str] = os.getenv("EVENT_GRID_ENDPOINT")
    EVENT_GRID_KEY: Optional[str] = os.getenv("EVENT_GRID_KEY")
    
    # Azure Storage (Blob for immutable logs)
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AUDIT_LOG_CONTAINER: str = os.getenv("AUDIT_LOG_CONTAINER", "audit-logs")
    
    # Azure Key Vault
    KEY_VAULT_URL: str = os.getenv("KEY_VAULT_URL", "https://your-keyvault.vault.azure.net/")
    
    # Microsoft Graph API
    GRAPH_CLIENT_ID: Optional[str] = os.getenv("GRAPH_CLIENT_ID")
    GRAPH_CLIENT_SECRET: Optional[str] = os.getenv("GRAPH_CLIENT_SECRET")
    GRAPH_TENANT_ID: Optional[str] = os.getenv("GRAPH_TENANT_ID")
    
    # Azure Speech Service
    SPEECH_KEY: Optional[str] = os.getenv("SPEECH_KEY")
    SPEECH_REGION: str = os.getenv("SPEECH_REGION", "eastus")
    
    # Application Insights
    APPLICATIONINSIGHTS_CONNECTION_STRING: Optional[str] = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    # Bot Service
    MICROSOFT_APP_ID: Optional[str] = os.getenv("MICROSOFT_APP_ID")
    MICROSOFT_APP_PASSWORD: Optional[str] = os.getenv("MICROSOFT_APP_PASSWORD")
    
    # Power Automate
    POWER_AUTOMATE_BASE_URL: str = os.getenv("POWER_AUTOMATE_BASE_URL", "https://prod-00.eastus.logic.azure.com")
    
    # Application Settings
    APP_NAME: str = "Azure AI Service Desk"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Confidence Scoring
    CONFIDENCE_THRESHOLD_AUTO_RESOLVE: float = 0.8
    CONFIDENCE_THRESHOLD_ESCALATE: float = 0.5
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Responsible AI
    ENABLE_CONTENT_SAFETY: bool = True
    ENABLE_PII_DETECTION: bool = True
    ENABLE_BIAS_TRACKING: bool = True
    ENABLE_AUDIT_LOGGING: bool = True


settings = Settings()
