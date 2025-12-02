"""
Simple but functional AI agent that actually works in development mode
Uses knowledge base retrieval and basic rule-based reasoning
This demonstrates the concept without requiring Azure OpenAI API keys
"""
import logging
import os
# Trigger reload for env vars
from typing import Dict, List, Optional, Any
from datetime import datetime

from .knowledge_base import get_knowledge_base, KnowledgeArticle
from .content_safety_service import get_content_safety_service
from openai import AsyncAzureOpenAI
from ..config.settings import settings

logger = logging.getLogger(__name__)


class SimpleAgent:
    """
    Functional AI agent using rule-based logic and knowledge base retrieval
    Provides intelligent responses without requiring external API calls
    """
    
    def __init__(self):
        self.kb = get_knowledge_base()
        self.client = AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version="2024-02-15-preview",
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        self.safety_service = get_content_safety_service()
        self.intent_patterns = self._initialize_intent_patterns()
        logger.info("Simple Agent initialized")
    
    def _initialize_intent_patterns(self) -> Dict[str, List[str]]:
        """Initialize intent detection patterns"""
        return {
            "password_reset": [
                "password", "reset", "forgot password", "can't login", "locked out",
                "change password", "forgot my password", "contraseña", "olvidé", "resetear"
            ],
            "vpn_issue": [
                "vpn", "remote access", "can't connect", "vpn not working",
                "vpn connection", "remote work", "conexión"
            ],
            "software_request": [
                "install", "software", "application", "program", "need software",
                "install application", "instalar", "programa"
            ],
            "email_problem": [
                "email", "outlook", "can't send", "can't receive", "mailbox",
                "email problem", "correo"
            ],
            "leave_balance": [
                "leave balance", "vacation days", "time off", "pto", "how many days",
                "leave remaining", "annual leave", "vacaciones", "días libres"
            ],
            "leave_request": [
                "request time off", "request leave", "book vacation", "take time off",
                "request holiday", "pedir vacaciones", "solicitar días"
            ],
            "payroll_query": [
                "payslip", "salary", "payroll", "payment", "pay", "wages",
                "when paid", "nómina", "sueldo", "pago", "recibo"
            ],
            "room_booking": [
                "book room", "meeting room", "conference room", "reserve room",
                "book meeting", "reservar sala", "sala de reuniones"
            ],
            "equipment_request": [
                "monitor", "keyboard", "chair", "desk", "equipment", "need equipment",
                "ergonomic", "teclado", "silla", "escritorio", "equipo"
            ],
            "parking_access": [
                "parking", "access card", "badge", "building access", "lost card",
                "parking space", "estacionamiento", "tarjeta", "acceso"
            ],
            "legal_document": [
                "nda", "contract", "agreement", "legal", "compliance", "regulation",
                "policy review", "contrato", "legal", "acuerdo"
            ],
            "expense_reimbursement": [
                "expense", "reimbursement", "receipt", "taxi", "uber", "travel",
                "meal", "reembolso", "gasto", "viático", "ticket"
            ]
        }
    
    async def categorize(self, message: str, language: str = "en") -> str:
        """Categorize the message into IT, HR, FACILITIES, LEGAL, or FINANCE using LLM"""
        try:
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_GPT4O_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant that categorizes user requests into one of the following categories: IT, HR, FACILITIES, LEGAL, FINANCE. You can process requests in English or Spanish. Respond with only the category name."},
                    {"role": "user", "content": f"Categorize the following request: '{message}'"}
                ],
                temperature=0.0,
                max_tokens=10
            )
            category = response.choices[0].message.content.strip().upper()
            
            category_map = {
                "IT": "it_support",
                "HR": "hr_inquiry",
                "FACILITIES": "facilities",
                "LEGAL": "legal",
                "FINANCE": "finance"
            }
            
            if category in category_map:
                mapped_category = category_map[category]
                logger.info(f"LLM categorized message as: {category} -> {mapped_category}")
                return mapped_category
            else:
                logger.warning(f"LLM returned unrecognised category: {category}. Defaulting to it_support.")
                return "it_support" # Fallback for unexpected LLM output
        except Exception as e:
            logger.error(f"Error during LLM categorization: {e}. Falling back to it_support.")
            return "it_support" # Fallback if LLM call fails
    
    def detect_intent(self, message: str) -> Optional[str]:
        """Detect the user's intent from the message"""
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return intent
        
        return None
    
    async def generate_response(self, message: str, language: str = "en") -> Dict[str, Any]:

        """
        Generate an intelligent response based on the message
        Returns: dict with response, confidence, category, kb_articles, reasoning
        """
        # 1. Content Safety Check
        safety_result = await self.safety_service.analyze_text(message)
        if not safety_result.is_safe:
            logger.warning(f"Message blocked by content safety: {safety_result.blocked_reason}")
            return {
                "response": f"I cannot process your request because it was flagged by our safety system: {safety_result.blocked_reason}. Please rephrase your request.",
                "confidence": 1.0,
                "category": "SECURITY",
                "intent": "security_violation",
                "kb_articles": [],
                "reasoning": f"Blocked by Azure Content Safety: {safety_result.blocked_reason}",
                "can_auto_resolve": True
            }

        # 2. Determine category
        category = await self.categorize(message, language)
        
        # 3. Detect intent
        intent = self.detect_intent(message)
        
        # 4. Search knowledge base with category filters
        kb_articles = await self.kb.search(message, category=category if category else None, limit=3)

        # 5. Translate articles if needed
        try:
            with open(r"C:\Users\ASUS\.gemini\my_debug.log", "a") as f:
                f.write(f"DEBUG_LOG: Language={language}, KB count={len(kb_articles)}\n")
        except Exception as e:
            print(f"Log error: {e}")

        logger.info(f"DEBUG: Language={language}, KB Articles count={len(kb_articles)}")
        
        if language.lower() not in ['en', 'english'] and kb_articles:
            logger.info("DEBUG: Calling _translate_articles")
            kb_articles = await self._translate_articles(kb_articles, language)
        
        # 6. Generate response based on intent and knowledge base
        response = self._compose_response(message, intent, category, kb_articles, language)
        
        # 7. Calculate confidence score
        confidence = self._calculate_confidence(intent, kb_articles)
        
        # 7. Generate reasoning
        reasoning = self._generate_reasoning(intent, category, kb_articles, confidence)
        
        # Metadata is now returned in the dict, not appended to text
        priority = 'High' if 'urgent' in message.lower() or 'asap' in message.lower() else 'Normal'

        return {
            "response": response,
            "confidence": confidence,
            "category": category,
            "intent": intent,
            "kb_articles": [a.model_dump(mode='json') for a in kb_articles],
            "reasoning": reasoning,
            "priority": priority,
            "can_auto_resolve": confidence >= 0.8
        }
    
    def _compose_response(
        self,
        message: str,
        intent: Optional[str],
        category: str,
        kb_articles: List[KnowledgeArticle],
        language: str = "en"
    ) -> str:
        """Compose a helpful response"""
        
        is_spanish = language.lower() in ['es', 'spanish']

        # Start with a friendly greeting
        response = "Entiendo que necesitas ayuda con " if is_spanish else "I understand you need help with "
        
        # Add intent-specific response
        # Add intent-specific response
        if intent == "password_reset":
            response += ("restablecer tu contraseña.\n\n" if is_spanish else "resetting your password.\n\n")
            if kb_articles:
                response += kb_articles[0].content
                response += ("\n\n✅ ¿Te gustaría que inicie el restablecimiento de contraseña por ti?" if is_spanish else "\n\n✅ Would you like me to initiate a password reset for you?")
            else:
                response += ("Aquí te explico cómo restablecer tu contraseña:\n" if is_spanish else "Here's how to reset your password:\n")
                response += ("1. Ve a https://password.company.com\n" if is_spanish else "1. Go to https://password.company.com\n")
                response += ("2. Haz clic en 'Olvidé mi contraseña'\n" if is_spanish else "2. Click 'Forgot Password'\n")
                response += ("3. Sigue las instrucciones del correo\n\n" if is_spanish else "3. Follow the email instructions\n\n")
                response += ("¿Quieres que te envíe un enlace de restablecimiento?" if is_spanish else "Would you like me to send you a reset link?")
        
        elif intent == "vpn_issue":
            response += ("problemas de conexión VPN.\n\n" if is_spanish else "VPN connection issues.\n\n")
            if kb_articles:
                response += kb_articles[0].content
            else:
                response += ("Prueba estos pasos:\n" if is_spanish else "Try these steps:\n")
                response += ("1. Verifica tu conexión a internet\n" if is_spanish else "1. Check your internet connection\n")
                response += ("2. Reinicia el cliente VPN\n" if is_spanish else "2. Restart the VPN client\n")
                response += ("3. Verifica que tienes la última versión instalada\n" if is_spanish else "3. Verify you have the latest version installed\n")
        
        elif intent == "leave_balance":
            response += ("consultar tu saldo de vacaciones.\n\n" if is_spanish else "checking your leave balance.\n\n")
            if kb_articles:
                response += kb_articles[0].content
            else:
                response += ("Para consultar tu saldo:\n" if is_spanish else "To check your leave balance:\n")
                response += ("1. Inicia sesión en https://hr.company.com\n" if is_spanish else "1. Log in to https://hr.company.com\n")
                response += ("2. Ve a 'Mi Perfil' > 'Licencias y Tiempo Libre'\n" if is_spanish else "2. Go to 'My Profile' > 'Leave & Time Off'\n")
                response += ("3. Mira tu saldo actual\n" if is_spanish else "3. View your current balance\n")
        
        elif intent == "room_booking":
            response += ("reservar una sala de reuniones.\n\n" if is_spanish else "booking a meeting room.\n\n")
            if kb_articles:
                response += kb_articles[0].content
            else:
                response += ("Para reservar una sala:\n" if is_spanish else "To book a meeting room:\n")
                response += ("1. Abre el Calendario de Outlook\n" if is_spanish else "1. Open Outlook Calendar\n")
                response += ("2. Crea una nueva reunión\n" if is_spanish else "2. Create a new meeting\n")
                response += ("3. Usa el 'Buscador de Salas' para seleccionar una disponible\n" if is_spanish else "3. Use 'Room Finder' to select an available room\n")
        
        elif intent == "expense_reimbursement":
            response += ("enviar un reembolso de gastos.\n\n" if is_spanish else "submitting an expense reimbursement.\n\n")
            if kb_articles:
                response += kb_articles[0].content
            else:
                response += ("Para enviar un gasto:\n" if is_spanish else "To submit an expense:\n")
                response += ("1. Inicia sesión en el Portal de Finanzas\n" if is_spanish else "1. Log in to the Finance Portal\n")
                response += ("2. Haz clic en 'Nuevo Informe de Gastos'\n" if is_spanish else "2. Click 'New Expense Report'\n")
                response += ("3. Sube tu recibo y completa los detalles\n" if is_spanish else "3. Upload your receipt and fill in the details\n")

        elif kb_articles:
            # Generic response using best-matching KB article
            article_prefix = "una" if is_spanish else ("an" if category in ["IT", "HR"] else "a")
            response += (f"{article_prefix} consulta de {category.lower()}.\n\n" if is_spanish else f"{article_prefix} {category.lower()} query.\n\n")
            response += f"**{kb_articles[0].title}**\n\n"
            response += kb_articles[0].content
            
            if len(kb_articles) > 1:
                response += (f"\n\n📚 Relacionado: {kb_articles[1].title}" if is_spanish else f"\n\n📚 Related: {kb_articles[1].title}")
        
        else:
            # Fallback response
            article_prefix = "un" if is_spanish else ("an" if category in ["IT", "HR"] else "a")
            response += (f"{article_prefix} problema de {category.lower()}.\n\n" if is_spanish else f"{article_prefix} {category.lower()} issue.\n\n")
            response += ("He categorizado tu solicitud y te conectaré con el equipo adecuado. " if is_spanish else "I've categorized your request and will connect you with the appropriate team. ")
            response += (f"Para consultas de {category}, el tiempo de respuesta típico es de 2-4 horas en horario laboral.\n\n" if is_spanish else f"For {category} queries, typical response time is 2-4 hours during business hours.\n\n")
            response += ("Mientras tanto, puedes:\n" if is_spanish else "In the meantime, you can:\n")
            response += ("- Consultar nuestras Preguntas Frecuentes en https://help.company.com\n" if is_spanish else "- Check our FAQ at https://help.company.com\n")
            response += (f"- Visitar el portal de {category} para solicitudes comunes\n" if is_spanish else f"- Visit the {category} portal for common requests\n")
            response += ("- Llamar a la línea de soporte para problemas urgentes" if is_spanish else "- Call the support hotline for urgent issues")
        
        return response
    
    def _calculate_confidence(self, intent: Optional[str], kb_articles: List[KnowledgeArticle]) -> float:
        """Calculate confidence score for the response"""
        confidence = 0.5  # Base confidence
        
        # Intent detected increases confidence
        if intent:
            confidence += 0.2
        
        # Knowledge base articles increase confidence
        if kb_articles:
            confidence += 0.15 * len(kb_articles)
        
        # Cap at 0.95 (never 100% confident without human verification)
        return min(confidence, 0.95)
    
    async def _translate_articles(self, articles: List[KnowledgeArticle], target_language: str) -> List[KnowledgeArticle]:
        try:
            with open(r"C:\Users\ASUS\.gemini\my_debug.log", "a") as f:
                f.write(f"DEBUG_LOG: Inside _translate_articles. Target: {target_language}\n")
        except: pass

        """Translate articles to target language using LLM"""
        try:
            # Prepare content for translation
            articles_text = "\n\n".join([f"ID: {a.id}\nTitle: {a.title}\nContent: {a.content}" for a in articles])
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_GPT4O_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": f"You are a professional translator. Translate the following Knowledge Base articles into {target_language}. Maintain the ID, Title, and Content structure exactly. Return ONLY the translated text in the same format."},
                    {"role": "user", "content": articles_text}
                ],
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content
            logger.info(f"LLM Translation Output:\n{translated_text}")
            
            # Parse back into articles using regex for robustness
            import re
            
            # Regex to find blocks starting with ID: ... Title: ... Content: ...
            # We split by ID: to get chunks
            chunks = re.split(r'(?:^|\n)ID:\s*', translated_text)
            
            translated_map = {}
            for chunk in chunks:
                if not chunk.strip(): continue
                
                # Extract ID (first line or up to newline)
                lines = chunk.split('\n', 1)
                current_id = lines[0].strip()
                rest = lines[1] if len(lines) > 1 else ""
                
                # Extract Title
                title_match = re.search(r'Title:\s*(.*?)(?:\nContent:|$)', rest, re.DOTALL)
                content_match = re.search(r'Content:\s*(.*)', rest, re.DOTALL)
                
                if title_match and content_match:
                    title = title_match.group(1).strip()
                    content = content_match.group(1).strip()
                    translated_map[current_id] = {"title": title, "content": content}

            logger.info(f"Parsed Translation Map: {translated_map.keys()}")

            # Update articles
            for article in articles:
                if article.id in translated_map:
                    article.title = translated_map[article.id]["title"]
                    article.content = translated_map[article.id]["content"]
            
            return articles
            
        except Exception as e:
            logger.error(f"Error translating articles: {e}", exc_info=True)
            return articles # Return original if translation fails

    def _generate_reasoning(
        self,
        intent: Optional[str],
        category: str,
        kb_articles: List[KnowledgeArticle],
        confidence: float
    ) -> str:
        """Generate explanation of reasoning process"""
        reasoning_parts = []
        
        reasoning_parts.append(f"1. Categorized as {category} based on keyword analysis")
        
        if intent:
            reasoning_parts.append(f"2. Detected intent: {intent.replace('_', ' ').title()}")
        else:
            reasoning_parts.append("2. No specific intent detected, using general response")
        
        if kb_articles:
            reasoning_parts.append(f"3. Found {len(kb_articles)} relevant knowledge base article(s)")
            reasoning_parts.append(f"   - Primary: {kb_articles[0].title}")
        else:
            reasoning_parts.append("3. No exact knowledge base match, using generic guidance")
        
        reasoning_parts.append(f"4. Confidence score: {confidence:.2%}")
        reasoning_parts.append(f"   - {'Can auto-resolve' if confidence >= 0.8 else 'Recommend human escalation'}")
        
        return "\n".join(reasoning_parts)


# Singleton instance
_simple_agent = None

def get_simple_agent() -> SimpleAgent:
    """Get singleton simple agent instance"""
    global _simple_agent
    if _simple_agent is None:
        _simple_agent = SimpleAgent()
    return _simple_agent
