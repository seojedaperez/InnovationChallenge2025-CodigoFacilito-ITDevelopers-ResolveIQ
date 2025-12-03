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
import asyncio
import json

logger = logging.getLogger(__name__)

class SimpleAgent:
    def __init__(self):
        self.kb = get_knowledge_base()
        self.safety_service = get_content_safety_service()
        try:
            self.client = AsyncAzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                http_client=httpx.AsyncClient(timeout=10.0)
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Azure OpenAI client: {e}. Running in offline mode.")
            self.client = None
            
        self.intent_patterns = {
            "password_reset": ["password", "reset", "forgot", "login", "access", "contraseña", "clave", "ingreso"],
            "vpn_issue": ["vpn", "connection", "connect", "network", "red", "conexión"],
            "leave_balance": ["leave", "vacation", "time off", "balance", "holiday", "vacaciones", "días libres"],
            "room_booking": ["room", "meeting", "book", "reserve", "conference", "sala", "reunión", "reserva"],
            "expense_reimbursement": ["expense", "reimbursement", "claim", "receipt", "money", "gastos", "reembolso", "factura"]
        }

    async def categorize(self, message: str, language: str = "en") -> List[str]:
        """Categorize the message into IT, HR, FACILITIES, LEGAL, or FINANCE using LLM"""
        import logging
        logger = logging.getLogger(__name__)
        try:
            if not self.client:
                logger.warning("Azure OpenAI client not available. Using fallback categorization.")
                return ["it_support"]

            # Retry logic for categorization
            max_retries = 3
            response = None
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    response = await self.client.chat.completions.create(
                        model=settings.AZURE_OPENAI_GPT4O_DEPLOYMENT,
                        messages=[
                        {"role": "system", "content": f"You are a helpful assistant that categorizes user requests into one or more of the following categories: IT, HR, FACILITIES, LEGAL, FINANCE. If the request is too vague or ambiguous to categorize (e.g., 'I have a problem', 'Help me'), respond with 'CLARIFICATION_NEEDED'. You can process requests in English or Spanish. Respond with the category names separated by commas (e.g., 'IT, HR')."},
                        {"role": "user", "content": f"Categorize the following request: '{message}'"}
                        ],
                        temperature=0.0,
                        max_tokens=20,
                        timeout=5.0
                    )
                    break
                except Exception as e:
                    last_error = e
                    logger.warning(f"Categorization attempt {attempt+1} failed: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
            
            if response is None:
                raise last_error or Exception("Categorization failed after retries")

            content = response.choices[0].message.content.strip().upper()
            raw_categories = [c.strip() for c in content.split(',')]
            
            category_map = {
            "IT": "it_support",
            "HR": "hr_inquiry",
            "FACILITIES": "facilities",
            "LEGAL": "legal",
            "FINANCE": "finance",
            "CLARIFICATION_NEEDED": "clarification_needed"
            }
            
            mapped_categories = []
            for cat in raw_categories:
                if cat in category_map:
                    mapped_categories.append(category_map[cat])
                else:
                    print("WARNING: ", f"LLM returned unrecognised category: {cat}")
            
            if not mapped_categories:
                 print("WARNING: ", f"No valid categories found in LLM response: {content}. Defaulting to it_support.")
                 return ["it_support"]

            print("INFO: ", f"LLM categorized message as: {raw_categories} -> {mapped_categories}")
            return mapped_categories

        except Exception as e:
            print("ERROR: ", f"Error during LLM categorization: {e}. Falling back to it_support.")
            return ["it_support"] # Fallback if LLM call fails
    
    def detect_intent(self, message: str) -> Optional[str]:
        """Detect the user's intent from the message"""
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return intent
        
        return None

    def _localize_block_reason(self, reason: str) -> str:
        """Translate block reason to Spanish"""
        reason_lower = reason.lower()
        if "pii" in reason_lower:
            return "Información Personal Identificable (PII) detectada"
        if "jailbreak" in reason_lower:
            return "Intento de manipulación del sistema detectado"
        if "hate" in reason_lower:
            return "Contenido de odio detectado"
        if "sexual" in reason_lower:
            return "Contenido sexual detectado"
        if "violence" in reason_lower:
            return "Contenido violento detectado"
        if "selfharm" in reason_lower:
            return "Contenido de autolesión detectado"
        return reason

    async def generate_response(self, message: str, language: str = "en", email_notifications: bool = False, user_email: str = None) -> Dict[str, Any]:
        """
        Generate an intelligent response based on the message
        Returns: dict with response, confidence, category, kb_articles, reasoning
        """
        import uuid
        categories = ["it_support"] # Default to avoid NameError
        print(f"DEBUG: generate_response called with message: {message}")
        
        # 1. Content Safety Check
        safety_result = await self.safety_service.analyze_text(message)
        if not safety_result.is_safe:
            logger.warning(f"Message blocked by content safety: {safety_result.blocked_reason}")
            
            is_spanish = language.lower() in ['es', 'spanish']
            blocked_msg_en = f"I cannot process your request because it was flagged by our safety system: {safety_result.blocked_reason}. Please rephrase your request."
            blocked_msg_es = f"No puedo procesar tu solicitud porque fue marcada por nuestro sistema de seguridad: {self._localize_block_reason(safety_result.blocked_reason)}. Por favor reformula tu solicitud."
            
            return {
                "response": blocked_msg_es if is_spanish else blocked_msg_en,
                "confidence": 1.0,
                "category": "SECURITY",
                "intent": "security_violation",
                "kb_articles": [],
                "reasoning": f"Blocked by Azure Content Safety: {safety_result.blocked_reason}",
                "can_auto_resolve": True,
                "ticket_id": None
            }

        # 2. Determine categories
        categories = await self.categorize(message, language)
        primary_category = categories[0] if categories else "it_support"
        
        # Handle Clarification Needed
        if "clarification_needed" in categories:
            is_spanish = language.lower() in ['es', 'spanish']
            return {
                "response": "¿Podrías darme más detalles sobre tu problema? Por ejemplo, ¿es algo relacionado con tu computadora, tu sueldo o el edificio?" if is_spanish else "Could you please provide more details about your issue? For example, is it related to your computer, your salary, or the building?",
                "confidence": 0.95,
                "category": "clarification_needed",
                "categories": ["clarification_needed"],
                "intent": "clarification",
                "kb_articles": [],
                "reasoning": "Request was too vague to categorize.",
                "can_auto_resolve": False,
                "ticket_id": None
            }

        # 3. Detect Intent (Rule-based)
        intent = self.detect_intent(message)
        # 4. Search Knowledge Base
        kb_articles = []
        if self.kb:
            try:
                kb_articles = await self.kb.search(message, category=primary_category)
            except Exception as e:
                logger.warning(f"Knowledge Base search failed: {e}")
                print(f"WARNING: Knowledge Base search failed: {e}")
            
        # 5. Compose Response
        response_text = await self._generate_llm_response(message, intent, categories, kb_articles, language)
        
        # 6. Calculate Confidence
        confidence = self._calculate_confidence(intent, kb_articles)
        
        # 7. Generate Reasoning
        reasoning = self._generate_reasoning(intent, categories, kb_articles, confidence)
        
        # 8. Generate Ticket ID
        ticket_id = f"TICKET-{uuid.uuid4().hex[:8].upper()}"
        
        # 9. Send Email Notification (if enabled)
        # Fallback for testing: if no user_email (guest mode), use sender address
        if not user_email and settings.EMAIL_SENDER_ADDRESS:
            print(f"DEBUG: No user_email provided (guest). Defaulting to sender address: {settings.EMAIL_SENDER_ADDRESS}")
            user_email = settings.EMAIL_SENDER_ADDRESS


        if email_notifications and user_email:
            # Run in background
            asyncio.create_task(self._send_email_notification(
                user_email=user_email,
                ticket_id=ticket_id,
                category=", ".join(categories),
                resolution=response_text,
                language=language,
                user_message=message
            ))
        
        return {
            "response": response_text,
            "confidence": confidence,
            "category": primary_category,
            "categories": categories,
            "intent": intent,
            "kb_articles": [a.dict() for a in kb_articles],
            "reasoning": reasoning,
            "can_auto_resolve": confidence >= 0.8,
            "ticket_id": ticket_id
        }

    async def _generate_llm_response(
        self,
        message: str,
        intent: Optional[str],
        categories: List[str],
        kb_articles: List[KnowledgeArticle],
        language: str = "en"
    ) -> str:
        """Generate a natural response using LLM, incorporating KB articles and ensuring correct language"""
        
        if not self.client:
            # Fallback to legacy static composition if LLM is unavailable
            return self._compose_response_legacy(message, intent, categories, kb_articles, language)

        try:
            # Prepare context from KB articles
            kb_context = ""
            if kb_articles:
                kb_context = "Here are some relevant knowledge base articles to help you answer:\n"
                for article in kb_articles:
                    kb_context += f"- Title: {article.title}\n  Content: {article.content}\n\n"
            
            system_prompt = f"""You are a helpful corporate AI assistant. 
            Your goal is to assist the user with their request based on the provided context.
            
            User Language: {language} (You MUST reply in this language).
            Detected Intent: {intent if intent else "General Inquiry"}
            Categories: {', '.join(categories)}
            
            {kb_context}
            
            Instructions:
            1. Answer the user's request directly and helpfully.
            2. If KB articles are provided, use them to formulate your answer.
            3. If no KB articles are relevant, give a polite general response acknowledging the category and offering to connect them to support.
            4. Be professional and concise.
            5. CRITICAL: The response MUST be in {language}.
            """

            response = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_GPT4O_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self._compose_response_legacy(message, intent, categories, kb_articles, language)

    def _compose_response_legacy(
        self,
        message: str,
        intent: Optional[str],
        categories: List[str],
        kb_articles: List[KnowledgeArticle],
        language: str = "en"
    ) -> str:
        """Compose a helpful response"""
        
        is_spanish = language.lower() in ['es', 'spanish']
        primary_category = categories[0] if categories else "it_support"

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
            cat_names = [self._get_category_name(c, language) for c in categories]
            cat_str = ", ".join(cat_names)
            
            article_prefix = "una" if is_spanish else ("an" if primary_category in ["IT", "HR"] else "a")
            response += (f"{article_prefix} consulta de {cat_str}.\n\n" if is_spanish else f"{article_prefix} {cat_str} query.\n\n")
            
            for i, article in enumerate(kb_articles):
                 response += f"**{article.title}**\n{article.content}\n\n"
                 if i >= 1: break # Limit to top 2 in text response
            
            if len(kb_articles) > 2:
                response += (f"\n\n📚 Relacionado: {kb_articles[2].title}" if is_spanish else f"\n\n📚 Related: {kb_articles[2].title}")
        
        else:
            # Fallback response
            cat_names = [self._get_category_name(c, language) for c in categories]
            cat_str = ", ".join(cat_names)
            
            article_prefix = "un" if is_spanish else ("an" if primary_category in ["IT", "HR"] else "a")
            response += (f"{article_prefix} problema de {cat_str}.\n\n" if is_spanish else f"{article_prefix} {cat_str} issue.\n\n")
            response += ("He categorizado tu solicitud y te conectaré con los equipos adecuados. " if is_spanish else "I've categorized your request and will connect you with the appropriate teams. ")
            response += (f"Para consultas de {cat_str}, el tiempo de respuesta típico es de 2-4 horas en horario laboral.\n\n" if is_spanish else f"For {cat_str} queries, typical response time is 2-4 hours during business hours.\n\n")
            response += ("Mientras tanto, puedes:\n" if is_spanish else "In the meantime, you can:\n")
            response += ("- Consultar nuestras Preguntas Frecuentes en https://help.company.com\n" if is_spanish else "- Check our FAQ at https://help.company.com\n")
            response += (f"- Visitar el portal de {primary_category} para solicitudes comunes\n" if is_spanish else f"- Visit the {primary_category} portal for common requests\n")
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
        categories: List[str],
        kb_articles: List[KnowledgeArticle],
        confidence: float
    ) -> str:
        """Generate explanation of reasoning process"""
        reasoning_parts = []
        
        reasoning_parts.append(f"1. Categorized as {', '.join(categories)} based on keyword analysis")
        
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

    def _get_category_name(self, category: str, language: str) -> str:
        """Get localized category name"""
        is_spanish = language.lower() in ['es', 'spanish']
        
        names = {
            "it_support": "Soporte TI" if is_spanish else "IT Support",
            "hr_inquiry": "Recursos Humanos" if is_spanish else "HR",
            "facilities": "Instalaciones" if is_spanish else "Facilities",
            "legal": "Legal" if is_spanish else "Legal",
            "finance": "Finanzas" if is_spanish else "Finance",
            "clarification_needed": "Clarificación Necesaria" if is_spanish else "Clarification Needed"
        }
        
        return names.get(category, category)

    async def _send_email_notification(self, user_email: str, ticket_id: str, category: str, resolution: str, language: str, user_message: str):
        """Send email notification with ticket details"""
        try:
            from .email_service import get_email_service
            email_service = get_email_service()
            import json
            import asyncio
            
            print(f"INFO: Preparing email content for {user_email}...")
            
            if not self.client:
                logger.warning("Azure OpenAI client not available. Skipping email generation.")
                return

            # Generate email content using LLM
            prompt = f"""You are a professional service desk agent. Write an email to the user regarding their ticket.
            
            Ticket ID: {ticket_id}
            Category: {category}
            User Message: {user_message}
            Resolution/Response: {resolution}
            Language: {language}
            
            The email should be professional, empathetic, and clear.
            IMPORTANT: Strictly base the email body on the provided Resolution/Response. 
            Do NOT invent details, forms, or procedures not mentioned in the Resolution/Response.
            Do NOT hallucinate health benefits or family enrollment unless explicitly mentioned in the Resolution/Response.
            
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
                response_format={"type": "json_object"},
                timeout=10.0
            )
            
            content = json.loads(response.choices[0].message.content)
            subject = content.get("subject", f"Ticket Update: {ticket_id}")
            body = content.get("body", resolution)
            
            # Send email (run in thread to avoid blocking)
            print(f"INFO: Sending email to {user_email} with subject: {subject}")
            await asyncio.to_thread(email_service.send_email, user_email, subject, body)
            print(f"INFO: Email task dispatched for {user_email}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            print(f"ERROR: Failed to send email notification: {e}")

_agent_instance = None

def get_simple_agent():
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = SimpleAgent()
    return _agent_instance