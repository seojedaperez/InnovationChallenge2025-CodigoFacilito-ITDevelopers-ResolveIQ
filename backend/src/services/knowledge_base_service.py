from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import json
from openai import AsyncAzureOpenAI

from ..config.settings import settings
from ..models.schemas import KnowledgeArticle, TicketCategory, KnowledgeArticleCreate, KnowledgeArticleUpdate
from .knowledge_base import KnowledgeBaseService as MockKnowledgeBaseService

logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    def __init__(self):
        self.mock_service = MockKnowledgeBaseService()
        self.use_azure_search = bool(settings.AZURE_SEARCH_ENDPOINT and settings.AZURE_SEARCH_KEY)
        
        # Initialize Azure OpenAI Client for semantic search
        self.openai_client = None
        if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_API_KEY:
            try:
                self.openai_client = AsyncAzureOpenAI(
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION
                )
                logger.info("KnowledgeBaseService: Azure OpenAI client initialized for semantic search")
            except Exception as e:
                logger.error(f"KnowledgeBaseService: Failed to initialize Azure OpenAI client: {e}")

    async def get_all_articles(self) -> List[KnowledgeArticle]:
        return await self.mock_service.get_all_articles()

    async def get_article(self, article_id: str) -> Optional[KnowledgeArticle]:
        return await self.mock_service.get_article(article_id)

    async def create_article(self, article: KnowledgeArticleCreate) -> KnowledgeArticle:
        return await self.mock_service.create_article(article)

    async def update_article(self, article_id: str, article_update: KnowledgeArticleUpdate) -> Optional[KnowledgeArticle]:
        return await self.mock_service.update_article(article_id, article_update)

    async def delete_article(self, article_id: str) -> bool:
        return await self.mock_service.delete_article(article_id)

    async def search(self, query: str, category: Optional[str] = None, limit: int = 5) -> List[KnowledgeArticle]:
        """
        Search for articles using LLM-based semantic matching if available, 
        falling back to keyword search.
        """
        # If OpenAI is not configured, fall back to keyword search
        if not self.openai_client:
            logger.warning("Azure OpenAI not configured, falling back to keyword search")
            return await self._keyword_search_fallback(query, category, limit)

        try:
            # Get all available articles (in a real app, we would use a vector DB)
            all_articles = await self.get_all_articles()
            
            # Prepare article summaries for the LLM
            articles_context = "\n".join([
                f"ID: {a.id} | Title: {a.title} | Content Preview: {a.content[:200]}... | Tags: {', '.join(a.tags)}"
                for a in all_articles
            ])

            # Construct the prompt
            system_prompt = """You are a helpful knowledge base assistant. 
            Your goal is to find the most relevant articles for a user's query.
            Return a JSON object with a key "relevant_article_ids" containing a list of the most relevant article IDs.
            If no articles are relevant, return an empty list.
            """
            
            user_prompt = f"""
            User Query: "{query}"
            Category Filter: {category if category else 'None'}
            
            Available Articles:
            {articles_context}
            
            Return the IDs of the top {limit} most relevant articles in JSON format.
            """

            # Call LLM
            response = await self.openai_client.chat.completions.create(
                model=settings.AZURE_OPENAI_GPT4O_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )

            # Parse response
            content = response.choices[0].message.content
            result = json.loads(content)
            relevant_ids = result.get("relevant_article_ids", [])
            
            # Retrieve full article objects
            found_articles = [a for a in all_articles if a.id in relevant_ids]
            
            # If LLM found nothing, try fallback just in case
            if not found_articles:
                logger.info("LLM found no matches, trying fallback keyword search")
                return await self._keyword_search_fallback(query, category, limit)
                
            return found_articles

        except Exception as e:
            logger.error(f"Error during LLM semantic search: {e}")
            return await self._keyword_search_fallback(query, category, limit)

    async def _keyword_search_fallback(self, query: str, category: Optional[str] = None, limit: int = 5) -> List[KnowledgeArticle]:
        """Fallback to simple keyword matching"""
        return await self.mock_service.search(query, category, limit)

# Global instance
_kb_service = None

def get_knowledge_base_service() -> KnowledgeBaseService:
    global _kb_service
    if _kb_service is None:
        _kb_service = KnowledgeBaseService()
    return _kb_service
