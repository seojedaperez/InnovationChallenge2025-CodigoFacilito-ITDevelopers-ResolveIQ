from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import sys

from ..config.settings import settings
from ..models.schemas import (
    TicketCreate, TicketResponse, HealthCheck, MetricsResponse,
    Ticket, TicketStatus, TicketCategory, ChannelType
)
from ..services.agent_orchestrator import AgentOrchestrator
from ..services.observability import setup_observability, trace_request

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator: AgentOrchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the FastAPI application"""
    global orchestrator
    
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Initialize observability
    if settings.APPLICATIONINSIGHTS_CONNECTION_STRING:
        setup_observability()
        logger.info("Application Insights configured")
    
    # Initialize agent orchestrator
    try:
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        logger.info("Agent orchestrator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent orchestrator: {e}")
        # Continue anyway for demo purposes
        orchestrator = None
    
    logger.info("Application startup complete")
    
    yield
    
    # Cleanup
    logger.info("Shutting down application")
    if orchestrator:
        await orchestrator.shutdown()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-Agent AI Service Desk with Azure AI Foundry Agent Service",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to all responses"""
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.debug(f"{request.method} {request.url.path} - {process_time:.3f}s")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheck, tags=["System"])
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    services = {
        "api": "healthy",
        "agent_orchestrator": "healthy" if orchestrator else "not_initialized",
    }
    
    return HealthCheck(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        services=services
    )


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Multi-Agent AI Service Desk for Microsoft Innovation Challenge",
        "documentation": "/docs",
        "health_check": "/health",
        "azure_services": [
            "Azure AI Foundry Agent Service",
            "Azure OpenAI (GPT-4o, o1-preview)",
            "Azure AI Search",
            "Azure Content Safety",
            "Azure Cosmos DB",
            "Azure SQL Database",
            "Azure Cache for Redis",
            "Azure Service Bus",
            "Azure Event Grid",
            "Microsoft Graph API",
            "Power Automate",
            "Azure Functions",
            "Azure Key Vault",
            "Azure Monitor & Application Insights",
            "Azure Bot Service",
            "Azure Speech Service",
            "Azure Container Apps",
            "Azure Front Door",
            "Azure Machine Learning"
        ]
    }


from ..services.auth_service import get_current_user

@app.post(f"{settings.API_PREFIX}/tickets", response_model=TicketResponse, tags=["Tickets"])
@trace_request
async def create_ticket(ticket_request: TicketCreate, user_payload: dict = Depends(get_current_user)):
    """
    Create a new support ticket and process it through the multi-agent system
    
    This endpoint:
    1. Creates a ticket in Cosmos DB
    2. Runs content safety checks
    3. Routes to appropriate domain specialist agent
    4. Executes runbooks if auto-resolvable
    5. Returns explanation graph and confidence score
    6. Escalates to human if needed
    """
    if not orchestrator:
        raise HTTPException(
            status_code=503,
            detail="Agent orchestrator not initialized. Please check configuration."
        )
    
    try:
        logger.info(f"Creating ticket for user {ticket_request.user_id} via {ticket_request.channel}")
        
        # Process ticket through multi-agent orchestration
        result = await orchestrator.process_ticket(ticket_request)
        
        logger.info(f"Ticket {result.ticket.id} processed - Status: {result.ticket.status}, Confidence: {result.ticket.confidence_score}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing ticket: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing ticket: {str(e)}")


@app.get(f"{settings.API_PREFIX}/tickets/{{ticket_id}}", response_model=Ticket, tags=["Tickets"])
@trace_request
async def get_ticket(ticket_id: str):
    """Get ticket details by ID"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        ticket = await orchestrator.get_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving ticket {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{settings.API_PREFIX}/metrics", response_model=MetricsResponse, tags=["Analytics"])
@trace_request
async def get_metrics():
    """Get service desk metrics and analytics"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        metrics = await orchestrator.get_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error retrieving metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{settings.API_PREFIX}/tickets/{{ticket_id}}/feedback", tags=["Tickets"])
@trace_request
async def submit_feedback(ticket_id: str, rating: int, comments: str = None):
    """Submit feedback for a resolved ticket (used for ML model retraining)"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = await orchestrator.submit_feedback(ticket_id, rating, comments)
        return {"status": "success", "message": "Feedback recorded", "ticket_id": ticket_id}
    except Exception as e:
        logger.error(f"Error submitting feedback for ticket {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{settings.API_PREFIX}/knowledge/search", tags=["Knowledge Base"])
@trace_request
async def search_knowledge(query: str, limit: int = 5):
    """Search knowledge base using Azure AI Search"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        results = await orchestrator.search_knowledge(query, limit)
        return {"query": query, "results": results}
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Bot Framework webhook endpoint
@app.post("/api/messages", tags=["Bot"])
async def bot_messages(request: Request):
    """Microsoft Bot Framework webhook endpoint for Teams integration"""
    logger.info("Received Bot Framework message")
    # Bot Framework integration will be implemented in later tasks
    return {"status": "received"}


# Voice channel webhook
@app.post("/api/voice/webhook", tags=["Voice"])
async def voice_webhook(request: Request):
    """Azure Speech Service webhook for voice channel"""
    logger.info("Received voice webhook")
    # Voice integration will be implemented in later tasks
    return {"status": "received"}


# Simple chat endpoint (working implementation)
@app.post(f"{settings.API_PREFIX}/chat", tags=["Chat"])
async def chat(user_id: str, message: str):
    """
    Simple chat endpoint that actually works in development mode
    Uses knowledge base retrieval and rule-based reasoning
    
    Example:
    POST /api/chat
    {
        "user_id": "user-001",
        "message": "I forgot my password and need to reset it"
    }
    """
    try:
        from ..services.simple_agent import get_simple_agent
        from ..services.storage_service import get_storage_service
        
        logger.info(f"Chat request from user {user_id}: {message[:100]}")
        
        # Get simple agent instance
        agent = get_simple_agent()
        storage = get_storage_service()
        
        # Generate intelligent response
        result = agent.generate_response(message)
        
        # Return structured response
        return {
            "user_id": user_id,
            "message": message,
            "response": result["response"],
            "confidence": result["confidence"],
            "category": result["category"],
            "intent": result["intent"],
            "can_auto_resolve": result["can_auto_resolve"],
            "reasoning": result["reasoning"],
            "kb_articles_used": len(result["kb_articles"]),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.src.api.main:app",
        host="0.0.0.0",
        port=5000,
        reload=settings.DEBUG
    )
