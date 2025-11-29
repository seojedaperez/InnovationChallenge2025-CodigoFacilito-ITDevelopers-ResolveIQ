import logging
from typing import Optional, Dict, Any
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from ..config.settings import settings

logger = logging.getLogger(__name__)

class FoundryService:
    """
    Service wrapper for Azure AI Foundry Agent Service
    """
    def __init__(self):
        self.project_client: Optional[AIProjectClient] = None
        self.agents: Dict[str, Any] = {}
        
    async def initialize(self):
        """Initialize the AI Project Client"""
        if not settings.AZURE_AI_PROJECT_CONNECTION_STRING:
            logger.warning("Azure AI Project connection string not found. Running in mock mode.")
            return

        try:
            self.project_client = AIProjectClient.from_connection_string(
                credential=DefaultAzureCredential(),
                conn_str=settings.AZURE_AI_PROJECT_CONNECTION_STRING,
            )
            logger.info("Azure AI Foundry Project Client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Azure AI Foundry Project Client: {e}")

    async def create_agent(self, name: str, model: str, instructions: str) -> Optional[Any]:
        """Create or retrieve an agent"""
        if not self.project_client:
            return None
            
        try:
            # This is a simplified representation of the actual SDK call
            # In a real scenario, we would check if agent exists or create new
            agent = await self.project_client.agents.create_agent(
                model=model,
                name=name,
                instructions=instructions
            )
            self.agents[name] = agent
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent {name}: {e}")
            return None

    async def create_thread(self):
        """Create a new conversation thread"""
        if not self.project_client:
            return None
        return await self.project_client.agents.create_thread()

    async def create_message(self, thread_id: str, content: str):
        """Add a message to the thread"""
        if not self.project_client:
            return None
        return await self.project_client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=content
        )

    async def run_agent(self, thread_id: str, agent_id: str):
        """Run the agent on the thread"""
        if not self.project_client:
            return None
        return await self.project_client.agents.create_run(
            thread_id=thread_id,
            assistant_id=agent_id
        )

_foundry_service = None

def get_foundry_service() -> FoundryService:
    global _foundry_service
    if _foundry_service is None:
        _foundry_service = FoundryService()
    return _foundry_service
