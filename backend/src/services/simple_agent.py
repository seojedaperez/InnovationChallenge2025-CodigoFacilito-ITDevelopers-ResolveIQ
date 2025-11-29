"""
Simple but functional AI agent that actually works in development mode
Uses knowledge base retrieval and basic rule-based reasoning
This demonstrates the concept without requiring Azure OpenAI API keys
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .knowledge_base import get_knowledge_base, KnowledgeArticle

logger = logging.getLogger(__name__)


class SimpleAgent:
    """
    Functional AI agent using rule-based logic and knowledge base retrieval
    Provides intelligent responses without requiring external API calls
    """
    
    def __init__(self):
        self.kb = get_knowledge_base()
        self.intent_patterns = self._initialize_intent_patterns()
        logger.info("Simple Agent initialized")
    
    def _initialize_intent_patterns(self) -> Dict[str, List[str]]:
        """Initialize intent detection patterns"""
        return {
            "password_reset": [
                "password", "reset", "forgot password", "can't login", "locked out",
                "change password", "forgot my password"
            ],
            "vpn_issue": [
                "vpn", "remote access", "can't connect", "vpn not working",
                "vpn connection", "remote work"
            ],
            "software_request": [
                "install", "software", "application", "program", "need software",
                "install application"
            ],
            "email_problem": [
                "email", "outlook", "can't send", "can't receive", "mailbox",
                "email problem"
            ],
            "leave_balance": [
                "leave balance", "vacation days", "time off", "pto", "how many days",
                "leave remaining", "annual leave"
            ],
            "leave_request": [
                "request time off", "request leave", "book vacation", "take time off",
                "request holiday"
            ],
            "payroll_query": [
                "payslip", "salary", "payroll", "payment", "pay", "wages",
                "when paid"
            ],
            "room_booking": [
                "book room", "meeting room", "conference room", "reserve room",
                "book meeting"
            ],
            "equipment_request": [
                "monitor", "keyboard", "chair", "desk", "equipment", "need equipment",
                "ergonomic"
            ],
            "parking_access": [
                "parking", "access card", "badge", "building access", "lost card",
                "parking space"
            ]
        }
    
    def categorize(self, message: str) -> str:
        """Categorize the message into IT, HR, or Facilities"""
        message_lower = message.lower()
        
        # IT keywords
        it_keywords = ["password", "vpn", "software", "install", "email", "outlook",
                      "computer", "laptop", "network", "printer", "login", "access",
                      "account", "application"]
        
        # HR keywords
        hr_keywords = ["leave", "vacation", "pto", "time off", "payroll", "payslip",
                      "salary", "pay", "holiday", "sick leave", "hr", "benefits"]
        
        # Facilities keywords
        fac_keywords = ["room", "meeting room", "book", "parking", "desk", "chair",
                       "monitor", "equipment", "building", "access card", "badge",
                       "facilities"]
        
        it_score = sum(1 for kw in it_keywords if kw in message_lower)
        hr_score = sum(1 for kw in hr_keywords if kw in message_lower)
        fac_score = sum(1 for kw in fac_keywords if kw in message_lower)
        
        if it_score >= hr_score and it_score >= fac_score:
            return "IT"
        elif hr_score >= fac_score:
            return "HR"
        else:
            return "FACILITIES"
    
    def detect_intent(self, message: str) -> Optional[str]:
        """Detect the user's intent from the message"""
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return intent
        
        return None
    
    def generate_response(self, message: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an intelligent response based on the message
        Returns: dict with response, confidence, category, kb_articles, reasoning
        """
        # Auto-categorize if not provided
        if not category:
            category = self.categorize(message)
        
        # Detect intent
        intent = self.detect_intent(message)
        
        # Search knowledge base
        kb_articles = self.kb.search(message, category=category if category else None, limit=2)
        
        # Generate response based on intent and knowledge base
        response = self._compose_response(message, intent, category, kb_articles)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(intent, kb_articles)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(intent, category, kb_articles, confidence)
        
        return {
            "response": response,
            "confidence": confidence,
            "category": category,
            "intent": intent,
            "kb_articles": kb_articles,
            "reasoning": reasoning,
            "can_auto_resolve": confidence >= 0.8
        }
    
    def _compose_response(
        self,
        message: str,
        intent: Optional[str],
        category: str,
        kb_articles: List[KnowledgeArticle]
    ) -> str:
        """Compose a helpful response"""
        
        # Start with a friendly greeting
        response = "I understand you need help with "
        
        # Add intent-specific response
        if intent == "password_reset":
            response += "resetting your password.\n\n"
            if kb_articles:
                response += kb_articles[0].content
                response += "\n\n✅ Would you like me to initiate a password reset for you?"
            else:
                response += "Here's how to reset your password:\n"
                response += "1. Go to https://password.company.com\n"
                response += "2. Click 'Forgot Password'\n"
                response += "3. Follow the email instructions\n\n"
                response += "Would you like me to send you a reset link?"
        
        elif intent == "vpn_issue":
            response += "VPN connection issues.\n\n"
            if kb_articles:
                response += kb_articles[0].content
            else:
                response += "Try these steps:\n"
                response += "1. Check your internet connection\n"
                response += "2. Restart the VPN client\n"
                response += "3. Verify you have the latest version installed\n"
        
        elif intent == "leave_balance":
            response += "checking your leave balance.\n\n"
            if kb_articles:
                response += kb_articles[0].content
            else:
                response += "To check your leave balance:\n"
                response += "1. Log in to https://hr.company.com\n"
                response += "2. Go to 'My Profile' > 'Leave & Time Off'\n"
                response += "3. View your current balance\n"
        
        elif intent == "room_booking":
            response += "booking a meeting room.\n\n"
            if kb_articles:
                response += kb_articles[0].content
            else:
                response += "To book a meeting room:\n"
                response += "1. Open Outlook Calendar\n"
                response += "2. Create a new meeting\n"
                response += "3. Use 'Room Finder' to select an available room\n"
        
        elif kb_articles:
            # Generic response using best-matching KB article
            response += f"a {category.lower()} query.\n\n"
            response += f"**{kb_articles[0].title}**\n\n"
            response += kb_articles[0].content
            
            if len(kb_articles) > 1:
                response += f"\n\n📚 Related: {kb_articles[1].title}"
        
        else:
            # Fallback response
            response += f"a {category.lower()} issue.\n\n"
            response += "I've categorized your request and will connect you with the appropriate team. "
            response += f"For {category} queries, typical response time is 2-4 hours during business hours.\n\n"
            response += "In the meantime, you can:\n"
            response += "- Check our FAQ at https://help.company.com\n"
            response += f"- Visit the {category} portal for common requests\n"
            response += "- Call the support hotline for urgent issues"
        
        # Add closing
        response += "\n\n---\n"
        response += f"**Category**: {category}\n"
        response += f"**Priority**: {'High' if 'urgent' in message.lower() or 'asap' in message.lower() else 'Normal'}\n"
        response += f"**Knowledge Base**: {len(kb_articles)} related article(s) found"
        
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


# Singleton instance
_simple_agent = None

def get_simple_agent() -> SimpleAgent:
    """Get singleton simple agent instance"""
    global _simple_agent
    if _simple_agent is None:
        _simple_agent = SimpleAgent()
    return _simple_agent
