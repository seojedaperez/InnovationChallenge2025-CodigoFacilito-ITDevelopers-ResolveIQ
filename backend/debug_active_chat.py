import asyncio
import sys
import os
import logging
from datetime import datetime

# Add backend to path
sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.services.agent_orchestrator import AgentOrchestrator
from src.models.schemas import TicketStatus

async def main():
    print("Initializing Orchestrator...")
    orchestrator = AgentOrchestrator()
    # We don't need full init, just loading data
    # _load_data is called in __init__
    
    print(f"Loaded {len(orchestrator.tickets_db)} tickets")
    
    # List all tickets to see what we have
    for t_id, t in orchestrator.tickets_db.items():
        print(f"Ticket: {t_id}, User: {t.user_id}, Status: {t.status}, Created: {t.created_at}")

    # Test get_latest_active_ticket logic
    user_id = "seojedaperez@outlook.es" 
    # Also try with the user_id from the persistence test if different
    
    print(f"\nSearching for active ticket for user: {user_id}")
    
    user_tickets = [
        t for t in orchestrator.tickets_db.values() 
        if t.user_id == user_id and t.status != TicketStatus.CLOSED
    ]
    
    print(f"Found {len(user_tickets)} active tickets")
    
    if user_tickets:
        user_tickets.sort(key=lambda x: x.created_at, reverse=True)
        latest = user_tickets[0]
        print(f"Latest active ticket: {latest.id}")
        
        # Check conversation
        conv = await orchestrator.get_conversation(latest.id)
        if conv:
            print(f"Conversation found with {len(conv.messages)} messages")
        else:
            print("Conversation NOT found")
    else:
        print("No active tickets found.")

if __name__ == "__main__":
    asyncio.run(main())
