"""
In-memory storage service for development mode
Provides working ticket and conversation storage without requiring Azure services
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict

from ..models.schemas import Ticket, AgentConversation, User

logger = logging.getLogger(__name__)


class InMemoryStorageService:
    """
    Simple in-memory storage that actually works in development mode
    Thread-safe for single-process use
    """
    
    def __init__(self):
        # Storage dictionaries
        self.tickets: Dict[str, Ticket] = {}
        self.conversations: Dict[str, AgentConversation] = {}
        self.users: Dict[str, User] = {}
        
        # Indexes for efficient querying
        self.tickets_by_user: Dict[str, List[str]] = defaultdict(list)
        self.tickets_by_status: Dict[str, List[str]] = defaultdict(list)
        self.tickets_by_category: Dict[str, List[str]] = defaultdict(list)
        
        logger.info("In-memory storage initialized")
    
    async def create_ticket(self, ticket: Ticket) -> Ticket:
        """Create a new ticket"""
        # Store the ticket
        self.tickets[ticket.id] = ticket
        
        # Update indexes
        self.tickets_by_user[ticket.user_id].append(ticket.id)
        self.tickets_by_status[ticket.status].append(ticket.id)
        if ticket.category:
            self.tickets_by_category[ticket.category].append(ticket.id)
        
        logger.info(f"Ticket created: {ticket.id} (user: {ticket.user_id}, category: {ticket.category})")
        return ticket
    
    async def get_ticket(self, ticket_id: str, user_id: str) -> Optional[Ticket]:
        """Get ticket by ID (validates user_id for security)"""
        ticket = self.tickets.get(ticket_id)
        if ticket and ticket.user_id == user_id:
            return ticket
        return None
    
    async def update_ticket(self, ticket: Ticket) -> Ticket:
        """Update an existing ticket"""
        old_ticket = self.tickets.get(ticket.id)
        if not old_ticket:
            raise ValueError(f"Ticket not found: {ticket.id}")
        
        # Update timestamp
        ticket.updated_at = datetime.utcnow()
        
        # If status changed, update index
        if old_ticket.status != ticket.status:
            self.tickets_by_status[old_ticket.status].remove(ticket.id)
            self.tickets_by_status[ticket.status].append(ticket.id)
        
        # Store updated ticket
        self.tickets[ticket.id] = ticket
        
        logger.info(f"Ticket updated: {ticket.id} (status: {ticket.status})")
        return ticket
    
    async def query_tickets(
        self,
        user_id: str,
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Ticket]:
        """Query tickets for a user with optional filters"""
        # Start with user's tickets
        ticket_ids = self.tickets_by_user.get(user_id, [])
        
        tickets = []
        for ticket_id in ticket_ids:
            ticket = self.tickets.get(ticket_id)
            if not ticket:
                continue
            
            # Apply filters
            if status and ticket.status != status:
                continue
            if category and ticket.category != category:
                continue
            
            tickets.append(ticket)
        
        # Sort by created_at (newest first) and limit
        tickets.sort(key=lambda t: t.created_at, reverse=True)
        return tickets[:limit]
    
    async def create_conversation(self, conversation: AgentConversation, user_id: str) -> AgentConversation:
        """Create a new agent conversation"""
        self.conversations[conversation.id] = conversation
        logger.info(f"Conversation created: {conversation.id}")
        return conversation
    
    async def get_conversation(self, conversation_id: str, user_id: str) -> Optional[AgentConversation]:
        """Get conversation by ID"""
        return self.conversations.get(conversation_id)
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    async def create_user(self, user: User) -> User:
        """Create a new user"""
        if user.id in self.users:
            logger.warning(f"User already exists: {user.id}")
            return self.users[user.id]
        
        self.users[user.id] = user
        logger.info(f"User created: {user.id}")
        return user
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        return {
            "total_tickets": len(self.tickets),
            "total_conversations": len(self.conversations),
            "total_users": len(self.users),
            "tickets_by_status": {status: len(ids) for status, ids in self.tickets_by_status.items()},
            "tickets_by_category": {cat: len(ids) for cat, ids in self.tickets_by_category.items()}
        }


# Singleton instance
_storage_service = None

def get_storage_service() -> InMemoryStorageService:
    """Get singleton storage service instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = InMemoryStorageService()
    return _storage_service
