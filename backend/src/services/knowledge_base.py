"""
Azure AI Search integration for knowledge base retrieval
"""
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

try:
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient
    from azure.search.documents.models import VectorizedQuery
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False
    SearchClient = None
    AzureKeyCredential = None
    VectorizedQuery = None

from ..config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeArticle:
    """Knowledge base article"""
    id: str
    category: str
    title: str
    content: str
    keywords: List[str]
    helpful_count: int = 0
    url: Optional[str] = None


class KnowledgeBaseService:
    """
    Knowledge base service using Azure AI Search
    """
    
    def __init__(self):
        self.client: Optional[SearchClient] = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize Azure AI Search client"""
        if not SEARCH_AVAILABLE:
            logger.warning("Azure Search SDK not installed, running in fallback mode")
            return
            
        if not settings.AZURE_SEARCH_ENDPOINT or not settings.AZURE_SEARCH_KEY:
            logger.warning("Azure Search credentials not found, running in fallback mode")
            return
            
        if settings.AZURE_SEARCH_ENDPOINT and settings.AZURE_SEARCH_KEY:
            try:
                credential = AzureKeyCredential(settings.AZURE_SEARCH_KEY)
                self.client = SearchClient(
                    endpoint=settings.AZURE_SEARCH_ENDPOINT,
                    index_name=settings.AZURE_SEARCH_INDEX_NAME,
                    credential=credential
                )
                logger.info("Azure AI Search client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Azure AI Search: {e}")

    async def search(self, query: str, category: Optional[str] = None, limit: int = 3) -> List[KnowledgeArticle]:
        """
        Search knowledge base using Azure AI Search
        """
        if not self.client:
            return self._mock_search(query, category, limit)
            
        try:
            # Build filter
            filter_expression = None
            if category:
                filter_expression = f"category eq '{category}'"
                
            # Execute search
            results = self.client.search(
                search_text=query,
                filter=filter_expression,
                top=limit,
                include_total_count=True
            )
            
            articles = []
            for result in results:
                articles.append(KnowledgeArticle(
                    id=result.get("id", ""),
                    category=result.get("category", "General"),
                    title=result.get("title", ""),
                    content=result.get("content", ""),
                    keywords=result.get("keywords", []),
                    url=result.get("url"),
                    helpful_count=result.get("helpful_count", 0)
                ))
                
            return articles
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return self._mock_search(query, category, limit)

    def _mock_search(self, query: str, category: Optional[str] = None, limit: int = 3) -> List[KnowledgeArticle]:
        """Fallback in-memory search for development"""
        # ... (Keep existing mock data for fallback)
        # Re-implementing a small subset of the mock data for fallback
        
        mock_articles = [
             KnowledgeArticle(
                id="it-001",
                category="IT",
                title="How to Reset Your Password",
                content="To reset your password: 1. Go to https://password.company.com 2. Click 'Forgot Password'",
                keywords=["password", "reset"]
            ),
            KnowledgeArticle(
                id="hr-001",
                category="HR",
                title="How to Check Your Leave Balance",
                content="Log in to the HR Portal: https://hr.company.com > 'My Profile' > 'Leave & Time Off'",
                keywords=["leave", "vacation"]
            )
        ]
        
        results = []
        query_lower = query.lower()
        
        for article in mock_articles:
            if category and article.category != category:
                continue
            
            if any(k in query_lower for k in article.keywords) or article.title.lower() in query_lower:
                results.append(article)
                
        return results[:limit]

# Singleton instance
_kb_service = None

def get_knowledge_base() -> KnowledgeBaseService:
    """Get singleton knowledge base instance"""
    global _kb_service
    if _kb_service is None:
        _kb_service = KnowledgeBaseService()
    return _kb_service
