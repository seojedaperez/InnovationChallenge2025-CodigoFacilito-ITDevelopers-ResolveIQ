import logging
import asyncio
from typing import Optional

try:
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory
    from azure.core.credentials import AzureKeyCredential
    from azure.identity import DefaultAzureCredential
    CONTENT_SAFETY_AVAILABLE = True
except ImportError:
    CONTENT_SAFETY_AVAILABLE = False
    ContentSafetyClient = None
    AnalyzeTextOptions = None
    TextCategory = None
    AzureKeyCredential = None
    DefaultAzureCredential = None

from ..config.settings import settings
from ..models.schemas import ContentSafetyResult

logger = logging.getLogger(__name__)


class ContentSafetyService:
    """
    Azure Content Safety integration for Responsible AI compliance.
    
    Provides:
    - Toxicity detection (hate, violence, sexual, self-harm)
    - Jailbreak attempt detection
    - PII detection
    - Custom prompt shields
    """
    
    def __init__(self):
        self.client: Optional[ContentSafetyClient] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Azure Content Safety client"""
        if not CONTENT_SAFETY_AVAILABLE:
            logger.warning("Azure Content Safety SDK not installed, running in fallback mode")
            self.client = None
            return
        
        if not settings.ENABLE_CONTENT_SAFETY:
            logger.warning("Content Safety is disabled in settings")
            return
        
        try:
            if settings.AZURE_CONTENT_SAFETY_KEY:
                credential = AzureKeyCredential(settings.AZURE_CONTENT_SAFETY_KEY)
            else:
                credential = DefaultAzureCredential()
            
            self.client = ContentSafetyClient(
                endpoint=settings.AZURE_CONTENT_SAFETY_ENDPOINT,
                credential=credential
            )
            logger.info("Content Safety client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Content Safety client: {e}")
            # Continue without Content Safety for development
            self.client = None
    
    async def analyze_text(self, text: str) -> ContentSafetyResult:
        """
        Analyze text for safety violations
        
        Returns:
            ContentSafetyResult with scores and blocking decision
        """
        # Always run local checks first (works even without Azure)
        jailbreak_detected = self._detect_jailbreak(text)
        pii_detected = self._detect_pii(text)
        
        # Initialize default scores
        hate_score = 0
        self_harm_score = 0
        sexual_score = 0
        violence_score = 0
        is_safe = True
        blocked_reason = None

        if self.client:
            try:
                request = AnalyzeTextOptions(text=text)
                
                # Analyze with Azure Content Safety
                response = await asyncio.wait_for(asyncio.to_thread(self.client.analyze_text, request), timeout=2.0)
                
                # Extract category scores (0-6 severity scale)
                hate_score = self._get_category_score(response, TextCategory.HATE)
                self_harm_score = self._get_category_score(response, TextCategory.SELF_HARM)
                sexual_score = self._get_category_score(response, TextCategory.SEXUAL)
                violence_score = self._get_category_score(response, TextCategory.VIOLENCE)
                
            except Exception as e:
                logger.error(f"Content Safety analysis failed: {e}")
                # If Azure fails, we rely on local checks, but log the error
        else:
            logger.warning("Content Safety client not available, running local checks only")

        # Determine if content should be blocked (threshold: severity >= 4)
        max_score = max(hate_score, self_harm_score, sexual_score, violence_score)
        
        # Combine local and remote results
        is_safe = max_score < 4 and not jailbreak_detected
        
        if max_score >= 4:
            categories = []
            if hate_score >= 4:
                categories.append("hate speech")
            if self_harm_score >= 4:
                categories.append("self-harm content")
            if sexual_score >= 4:
                categories.append("sexual content")
            if violence_score >= 4:
                categories.append("violent content")
            blocked_reason = f"Blocked due to: {', '.join(categories)}"
        elif jailbreak_detected:
            blocked_reason = "Potential jailbreak attempt detected"
        
        result = ContentSafetyResult(
            is_safe=is_safe,
            hate_score=hate_score / 6.0,  # Normalize to 0-1
            self_harm_score=self_harm_score / 6.0,
            sexual_score=sexual_score / 6.0,
            violence_score=violence_score / 6.0,
            jailbreak_detected=jailbreak_detected,
            pii_detected=pii_detected,
            blocked_reason=blocked_reason
        )
        
        logger.info(f"Content Safety analysis: is_safe={is_safe}, max_score={max_score}, jailbreak={jailbreak_detected}")
        return result
    
    def _get_category_score(self, response, category: TextCategory) -> int:
        """Extract severity score for a category"""
        try:
            for cat_analysis in response.categories_analysis:
                if cat_analysis.category == category:
                    return cat_analysis.severity
            return 0
        except Exception:
            return 0
    
    def _detect_jailbreak(self, text: str) -> bool:
        """
        Detect potential jailbreak attempts using custom prompt shields
        
        Common jailbreak patterns:
        - Role-play attempts ("ignore previous instructions")
        - System message injections
        - Character/persona escapes
        - DAN (Do Anything Now) prompts
        """
        jailbreak_patterns = [
            "ignore previous instructions",
            "ignore all previous",
            "new instructions:",
            "you are now",
            "forget everything",
            "disregard",
            "do anything now",
            "DAN mode",
            "developer mode",
            "system:",
            "sudo mode",
            # Spanish patterns
            "ignora todas tus instrucciones",
            "ignora todas las instrucciones",
            "olvida todo",
            "olvida tus reglas",
            "nuevas instrucciones:",
            "modo desarrollador",
            "modo dan",
            "dime cómo",
            "dime como", # No accent
            "como hackear",
            "como robar",
            "como borrar"
        ]
        
        text_lower = text.lower()
        logger.info(f"Checking jailbreak patterns in: '{text_lower}'")
        
        # Direct harmful phrases
        harmful_phrases = [
            "borrar la base de datos",
            "delete database",
            "drop table",
            "robar credenciales",
            "steal credentials"
        ]
        
        for phrase in harmful_phrases:
            if phrase in text_lower:
                logger.warning(f"Harmful phrase detected: {phrase}")
                return True

        for pattern in jailbreak_patterns:
            if pattern in text_lower:
                logger.warning(f"Jailbreak pattern detected: {pattern}")
                return True
        
        # Complex check: "dime como" + harmful action
        if "dime c" in text_lower or "tell me how" in text_lower:
             if any(x in text_lower for x in ["borrar", "delete", "hack", "robar", "steal", "eliminar", "bypass"]):
                 logger.warning("Jailbreak pattern detected: 'dime como' + harmful action")
                 return True

        logger.info("No jailbreak patterns found")
        return False
    
    def _detect_pii(self, text: str) -> bool:
        """
        Detect potential PII in text (basic implementation)
        
        In production, use Azure AI Language PII detection
        """
        if not settings.ENABLE_PII_DETECTION:
            return False
        
        # Simple pattern matching (production would use Azure AI Language)
        import re
        
        patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{16}\b',  # Credit card
            r'\b[A-Z]{2}\d{6,8}\b',  # Passport-like
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                logger.warning("Potential PII detected in text")
                return True
        
        return False
    
    def _mock_safe_result(self) -> ContentSafetyResult:
        """Return safe result for development/testing"""
        return ContentSafetyResult(
            is_safe=True,
            hate_score=0.0,
            self_harm_score=0.0,
            sexual_score=0.0,
            violence_score=0.0,
            jailbreak_detected=False,
            pii_detected=False
        )


# Singleton instance
_content_safety_service = None

def get_content_safety_service() -> ContentSafetyService:
    """Get singleton Content Safety service instance"""
    global _content_safety_service
    if _content_safety_service is None:
        _content_safety_service = ContentSafetyService()
    return _content_safety_service
