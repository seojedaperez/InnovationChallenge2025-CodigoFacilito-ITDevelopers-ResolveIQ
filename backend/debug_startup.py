import asyncio
import sys
import os
import logging

# Add backend to path
sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.services.agent_orchestrator import AgentOrchestrator

async def main():
    print("Attempting to initialize AgentOrchestrator...")
    try:
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        print("Initialization SUCCESS")
    except Exception as e:
        print(f"Initialization FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
