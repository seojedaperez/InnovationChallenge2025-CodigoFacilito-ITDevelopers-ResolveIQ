"""
Simple but functional AI agent that actually works in development mode
Uses knowledge base retrieval and basic rule-based reasoning
This demonstrates the concept without requiring Azure OpenAI API keys
"""
import logging
import os
import httpx
# Trigger reload for env vars
from typing import Dict, List, Optional, Any
from datetime import datetime

from .knowledge_base import get_knowledge_base, KnowledgeArticle
from .content_safety_service import get_content_safety_service
from openai import AsyncAzureOpenAI
from ..config.settings import settings

logger = logging.getLogger(__name__)



class SimpleAgent:
    def __init__(self):
        self.kb = get_knowledge_base()
        self.safety_service = get_content_safety_service()
        self.client = AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            http_client=httpx.AsyncClient()
        )
        self.intent_patterns = {
            "password_reset": ["password", "reset", "forgot", "login", "access", "contraseña", "clave", "ingreso"],
            "vpn_issue": ["vpn", "connection", "connect", "network", "red", "conexión"],
            "leave_balance": ["leave", "vacation", "time off", "balance", "holiday", "vacaciones", "días libres"],
            "room_booking": ["room", "meeting", "book", "reserve", "conference", "sala", "reunión", "reserva"],
            "expense_reimbursement": ["expense", "reimbursement", "claim", "receipt", "money", "gastos", "reembolso", "factura"]
        }

    async def categorize(self, message: str, language: str = "en") -> str:
        """Categorize the message into IT, HR, FACILITIES, LEGAL, or FINANCE using LLM"""
        import logging
        logger = logging.getLogger(__name__)
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
                print("INFO: ", f"LLM categorized message as: {category} -> {mapped_category}")
                return mapped_category
            else:
                print("WARNING: ", f"LLM returned unrecognised category: {category}. Defaulting to it_support.")
                return "it_support" # Fallback for unexpected LLM output
        except Exception as e:
            print("ERROR: ", f"Error during LLM categorization: {e}. Falling back to it_support.")
            return "it_support" # Fallback if LLM call fails
    
    def detect_intent(self, message: str) -> Optional[str]:
        """Detect the user's intent from the message"""
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return intent
        
        return None
    
    async def generate_response(self, message: str, language: str = "en", email_notifications: bool = False, user_email: str = None) -> Dict[str, Any]:
        import logging
        logger = logging.getLogger(__name__)
        """
        Generate an intelligent response based on the message
        Returns: dict with response, confidence, category, kb_articles, reasoning
        """
        import logging
        logger = logging.getLogger(__name__)
        # 1. Content Safety Check
        safety_result = await self.safety_service.analyze_text(message)
        if not safety_result.is_safe:
            print("WARNING: ", f"Message blocked by content safety: {safety_result.blocked_reason}")


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
        
        # Metadata is now returned in the dict, not appended to text
        priority = 'High' if 'urgent' in message.lower() or 'asap' in message.lower() else 'Normal'

        # Translate KB articles if needed
        # print("INFO: ", f"Translating articles to {language}")
        translated_kb_articles = await self._translate_articles(kb_articles, language)

        # 5. Generate response based on intent and knowledge base
        # Use translated articles for the response text
        response = self._compose_response(message, intent, category, translated_kb_articles, language)
        
        # 6. Calculate confidence score
        confidence = self._calculate_confidence(intent, translated_kb_articles)
        
        # 7. Generate reasoning
        reasoning = self._generate_reasoning(intent, category, translated_kb_articles, confidence)

        # Send email notification if enabled

        # Generate ticket ID
        import uuid
        ticket_id = f"TICKET-{str(uuid.uuid4())[:8].upper()}"
        # Send email notification if enabled
        if email_notifications and user_email:
            import asyncio
            # print(f"INFO: Scheduling email notification for {user_email}")
            asyncio.create_task(self._send_email_notification(user_email, ticket_id, category, response, language))

        return {
            "response": response,
            "confidence": confidence,
            "category": category,
            "intent": intent,
            "kb_articles": [a.model_dump(mode='json') for a in translated_kb_articles if (a.relevance_score or 0) >= 5],
            "reasoning": reasoning,
            "priority": priority,
            "can_auto_resolve": confidence >= 0.8,
            "ticket_id": ticket_id
        }

    async def _translate_articles(self, articles: List[KnowledgeArticle], target_language: str) -> List[KnowledgeArticle]:
        """Translate KB articles to target language using LLM"""
        import logging
        logger = logging.getLogger(__name__)
        print("INFO: ", f"Starting translation for {len(articles)} articles to '{target_language}'")
        
        if not articles:
            return articles
            
        if target_language.lower() in ['en', 'english']:
            return articles
            
        translated_articles = []
        for article in articles:
            import logging
            logger = logging.getLogger(__name__)
            try:
                # Create a copy to avoid modifying the original in cache/memory
                article_copy = article.model_copy()
                
                prompt = f"""Translate the following Knowledge Base article title and content to {target_language}. If the text is already in {target_language}, return it exactly as is.
                Maintain the technical meaning and formatting.
                
                Title: {article.title}
                Content: {article.content}
                
                Respond in JSON format: {{ "title": "translated_title", "content": "translated_content" }} """

                print("INFO: ", f"Translating article: {article.title}")
                
                response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_GPT4O_DEPLOYMENT,
                messages=[
                {"role": "system", "content": "You are a helpful translator for IT support articles. Output valid JSON only."},
                {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
                )
                
                import json
                result = json.loads(response.choices[0].message.content)
                print("INFO: ", f"Translation result: {result}")
                
                article_copy.title = result.get("title", article.title)
                article_copy.content = result.get("content", article.content)
                translated_articles.append(article_copy)
            except Exception as e:
                print("ERROR: ", f"Error translating article {article.id}: {e}", exc_info=True)
                translated_articles.append(article)
                
        return translated_articles
    
    def _get_category_name(self, category: str, language: str) -> str:
        is_spanish = "spanish" in language.lower() or "espa" in language.lower()
        
        categories_en = {
            "it_support": "IT Support",
            "hr_inquiry": "HR Inquiry",
            "facilities": "Facilities",
            "legal": "Legal",
            "finance": "Finance"
        }
        
        categories_es = {
            "it_support": "Soporte TI",
            "hr_inquiry": "Recursos Humanos",
            "facilities": "Instalaciones",
            "legal": "Legal",
            "finance": "Finanzas"
        }
        
        cat_key = category.lower()
        if is_spanish:
            return categories_es.get(cat_key, category)
        return categories_en.get(cat_key, category)

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
            response += (f"{article_prefix} consulta de {self._get_category_name(category, language)}.\n\n" if is_spanish else f"{article_prefix} {self._get_category_name(category, language)} query.\n\n")
            response += f"**{kb_articles[0].title}**\n\n"
            response += kb_articles[0].content
            
            if len(kb_articles) > 1:
                response += (f"\n\n📚 Relacionado: {kb_articles[1].title}" if is_spanish else f"\n\n📚 Related: {kb_articles[1].title}")
        
        else:
            # Fallback response
            article_prefix = "un" if is_spanish else ("an" if category in ["IT", "HR"] else "a")
            response += (f"{article_prefix} problema de {self._get_category_name(category, language)}.\n\n" if is_spanish else f"{article_prefix} {self._get_category_name(category, language)} issue.\n\n")
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


    async def _send_email_notification(self, user_email: str, ticket_id: str, category: str, resolution: str, language: str):
        """Send email notification with ticket details"""
        try:
            from .email_service import get_email_service
            email_service = get_email_service()
            import json
            import asyncio
            
            # Generate email content using LLM
            prompt = f"""You are a professional service desk agent. Write an email to the user regarding their ticket.
            
            Ticket ID: {ticket_id}
            Category: {category}
            Resolution/Response: {resolution}
            Language: {language}
            
            The email should be professional, empathetic, and clear.
            Subject: Update on your ticket {ticket_id}
            Body: HTML format.
            
            Return ONLY the JSON with keys "subject" and "body".
            """
            
            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_GPT4O_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content = json.loads(response.choices[0].message.content)
            subject = content.get("subject", f"Ticket Update: {ticket_id}")
            body = content.get("body", resolution)
            
            # Send email (run in thread to avoid blocking)
            # print(f"INFO: Sending email to {user_email}...")
            await asyncio.to_thread(email_service.send_email, user_email, subject, body)
            
        except Exception as e:
            print(f"ERROR: Failed to send email notification: {e}")

# Singleton instance
_simple_agent = None

def get_simple_agent() -> SimpleAgent:
    """Get singleton simple agent instance"""
    global _simple_agent
    if _simple_agent is None:
        _simple_agent = SimpleAgent()
    return _simple_agent