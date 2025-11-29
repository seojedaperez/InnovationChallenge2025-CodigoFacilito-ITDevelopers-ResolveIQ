import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.identity import DefaultAzureCredential

from ..config.settings import settings
from ..models.schemas import Ticket, AgentConversation, User

logger = logging.getLogger(__name__)


class CosmosDBService:
    """
    Azure Cosmos DB service for high-throughput operational data
    
    Containers:
    - tickets: Partitioned by userId
    - conversations: Partitioned by userId  
    - users: Partitioned by id
    - knowledge_articles: Partitioned by category
    - confidence_scores: Partitioned by userId
    """
    
    def __init__(self):
        self.client: Optional[CosmosClient] = None
        self.database = None
        self.containers = {}
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Cosmos DB client and database"""
        try:
            if settings.AZURE_COSMOS_KEY:
                self.client = CosmosClient(
                    url=settings.AZURE_COSMOS_ENDPOINT,
                    credential=settings.AZURE_COSMOS_KEY
                )
            else:
                # Use Managed Identity for production
                credential = DefaultAzureCredential()
                self.client = CosmosClient(
                    url=settings.AZURE_COSMOS_ENDPOINT,
                    credential=credential
                )
            
            # Get or create database
            self.database = self.client.create_database_if_not_exists(
                id=settings.AZURE_COSMOS_DATABASE_NAME
            )
            
            # Initialize containers
            self._initialize_containers()
            
            logger.info(f"Cosmos DB initialized: {settings.AZURE_COSMOS_DATABASE_NAME}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB: {e}")
            # Continue without Cosmos for development
            self.client = None
    
    def _initialize_containers(self):
        """Create containers if they don't exist"""
        if not self.database:
            return
        
        container_configs = [
            {
                "id": "tickets",
                "partition_key": PartitionKey(path="/userId"),
                "default_ttl": None  # No auto-expiration
            },
            {
                "id": "conversations",
                "partition_key": PartitionKey(path="/userId"),
                "default_ttl": 7776000  # 90 days
            },
            {
                "id": "users",
                "partition_key": PartitionKey(path="/id"),
                "default_ttl": None
            },
            {
                "id": "knowledge_articles",
                "partition_key": PartitionKey(path="/category"),
                "default_ttl": None
            },
            {
                "id": "confidence_scores",
                "partition_key": PartitionKey(path="/userId"),
                "default_ttl": 2592000  # 30 days
            }
        ]
        
        for config in container_configs:
            try:
                container = self.database.create_container_if_not_exists(
                    id=config["id"],
                    partition_key=config["partition_key"],
                    default_ttl=config.get("default_ttl")
                )
                self.containers[config["id"]] = container
                logger.info(f"Container initialized: {config['id']}")
            except Exception as e:
                logger.error(f"Failed to create container {config['id']}: {e}")
    
    async def create_ticket(self, ticket: Ticket) -> Ticket:
        """Create a new ticket"""
        if not self.containers.get("tickets"):
            logger.warning("Cosmos DB not available, using mock storage")
            return ticket
        
        try:
            ticket_dict = ticket.model_dump()
            ticket_dict["userId"] = ticket.user_id  # Map for Partition Key
            ticket_dict["partition_key"] = ticket.user_id
            
            self.containers["tickets"].create_item(body=ticket_dict)
            logger.info(f"Ticket created: {ticket.id}")
            return ticket
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create ticket: {e}")
            raise
    
    async def get_ticket(self, ticket_id: str, user_id: str) -> Optional[Ticket]:
        """Get ticket by ID and partition key (user_id)"""
        if not self.containers.get("tickets"):
            return None
        
        try:
            item = self.containers["tickets"].read_item(
                item=ticket_id,
                partition_key=user_id
            )
            return Ticket(**item)
            
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Ticket not found: {ticket_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to get ticket: {e}")
            return None
    
    async def update_ticket(self, ticket: Ticket) -> Ticket:
        """Update an existing ticket"""
        if not self.containers.get("tickets"):
            return ticket
        
        try:
            ticket.updated_at = datetime.utcnow()
            ticket_dict = ticket.model_dump()
            ticket_dict["userId"] = ticket.user_id  # Map for Partition Key
            ticket_dict["partition_key"] = ticket.user_id
            
            self.containers["tickets"].replace_item(
                item=ticket.id,
                body=ticket_dict
            )
            logger.info(f"Ticket updated: {ticket.id}")
            return ticket
            
        except Exception as e:
            logger.error(f"Failed to update ticket: {e}")
            raise
    
    async def query_tickets(
        self, 
        user_id: str, 
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Ticket]:
        """Query tickets for a user with optional filters"""
        if not self.containers.get("tickets"):
            return []
        
        try:
            query = "SELECT * FROM c WHERE c.userId = @user_id"
            parameters = [{"name": "@user_id", "value": user_id}]
            
            if status:
                query += " AND c.status = @status"
                parameters.append({"name": "@status", "value": status})
            
            if category:
                query += " AND c.category = @category"
                parameters.append({"name": "@category", "value": category})
            
            query += " ORDER BY c.created_at DESC"
            
            items = self.containers["tickets"].query_items(
                query=query,
                parameters=parameters,
                partition_key=user_id,
                max_item_count=limit
            )
            
            return [Ticket(**item) for item in items]
            
        except Exception as e:
            logger.error(f"Failed to query tickets: {e}")
            return []
    
    async def create_conversation(self, conversation: AgentConversation, user_id: str) -> AgentConversation:
        """Create a new agent conversation"""
        if not self.containers.get("conversations"):
            return conversation
        
        try:
            conv_dict = conversation.model_dump()
            conv_dict["userId"] = user_id
            conv_dict["partition_key"] = user_id
            
            self.containers["conversations"].create_item(body=conv_dict)
            logger.info(f"Conversation created: {conversation.id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            raise
    
    async def get_conversation(self, conversation_id: str, user_id: str) -> Optional[AgentConversation]:
        """Get conversation by ID"""
        if not self.containers.get("conversations"):
            return None
        
        try:
            item = self.containers["conversations"].read_item(
                item=conversation_id,
                partition_key=user_id
            )
            return AgentConversation(**item)
            
        except exceptions.CosmosResourceNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Failed to get conversation: {e}")
            return None
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        if not self.containers.get("users"):
            return None
        
        try:
            item = self.containers["users"].read_item(
                item=user_id,
                partition_key=user_id
            )
            return User(**item)
            
        except exceptions.CosmosResourceNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    async def create_user(self, user: User) -> User:
        """Create a new user"""
        if not self.containers.get("users"):
            return user
        
        try:
            user_dict = user.model_dump()
            user_dict["partition_key"] = user.id
            
            self.containers["users"].create_item(body=user_dict)
            logger.info(f"User created: {user.id}")
            return user
            
        except exceptions.CosmosResourceExistsError:
            logger.warning(f"User already exists: {user.id}")
            return user
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise


# Singleton instance
_cosmos_service = None

def get_cosmos_service() -> CosmosDBService:
    """Get singleton Cosmos DB service instance"""
    global _cosmos_service
    if _cosmos_service is None:
        _cosmos_service = CosmosDBService()
    return _cosmos_service
