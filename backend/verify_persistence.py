import asyncio
import sys
import os
import json
from datetime import datetime

# Add backend to path (current directory)
sys.path.append(os.getcwd())

from src.services.agent_orchestrator import AgentOrchestrator
from src.models.schemas import TicketCreate, ChannelType, TicketPriority
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    print("Testing Ticket Persistence...")
    
    # 1. Initialize Orchestrator and create a ticket
    orchestrator = AgentOrchestrator()
    # Mock initialize to avoid external calls
    orchestrator.initialized = True 
    
    ticket_request = TicketCreate(
        user_id="test-user-persist",
        description="This is a test ticket for persistence verification.",
        channel=ChannelType.WEB,
        priority=TicketPriority.MEDIUM
    )
    
    print("\nCreating ticket...")
    # We need to mock _run_safety_check and others to avoid errors without full init
    orchestrator._run_safety_check = lambda x: asyncio.sleep(0, result=True)
    orchestrator._categorize_ticket = lambda x, y: asyncio.sleep(0, result=("it_support", []))
    orchestrator._route_to_specialist = lambda w, x, y, z: asyncio.sleep(0, result=("Response", False))
    orchestrator._calculate_confidence = lambda x, y, z: asyncio.sleep(0, result=0.95)
    orchestrator._notify_human_agent = lambda x: asyncio.sleep(0)
    orchestrator._create_escalation_response = lambda x, y: None
    orchestrator._generate_explanation_graph = lambda x: None
    orchestrator._determine_next_steps = lambda x: []
    
    response = await orchestrator.process_ticket(ticket_request)
    ticket_id = response.ticket.id
    print(f"Ticket created: {ticket_id}")
    
    # 2. Verify file exists
    file_path = os.path.join(os.getcwd(), "data", "tickets.json")
    if os.path.exists(file_path):
        print(f"tickets.json exists at {file_path}")
    else:
        print("ERROR: tickets.json not found!")
        return

    # 3. Create a NEW Orchestrator instance (simulating restart)
    print("\nSimulating restart (creating new Orchestrator)...")
    new_orchestrator = AgentOrchestrator()
    
    # 4. Verify ticket is loaded
    if ticket_id in new_orchestrator.tickets_db:
        loaded_ticket = new_orchestrator.tickets_db[ticket_id]
        print(f"SUCCESS: Ticket {ticket_id} loaded from persistence.")
        print(f"Description: {loaded_ticket.description}")
    else:
        print(f"ERROR: Ticket {ticket_id} NOT found after restart.")

if __name__ == "__main__":
    asyncio.run(main())
