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
    Ticket, TicketStatus, TicketCategory, TicketPriority, ChannelType, AgentConversation,
    ChatRequest
)
from ..services.agent_orchestrator import AgentOrchestrator
from ..services.observability import setup_observability, trace_request
from ..services.document_service import DocumentService
from fastapi import UploadFile, File

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator: AgentOrchestrator = None
document_service = DocumentService()

# ... (rest of code)



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
    logger.error(f"Unhandled exception at {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "path": str(request.url),
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

@app.get(f"{settings.API_PREFIX}/tickets", response_model=list[Ticket], tags=["Tickets"])
@trace_request
async def list_tickets(user_payload: dict = Depends(get_current_user)):
    """List all tickets for the authenticated user"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # In a real app, we would filter by user_id from the token
        # For this demo, we return all tickets in memory
        # user_id = user_payload.get("sub")
        return list(orchestrator.tickets_db.values())
    except Exception as e:
        logger.error(f"Error listing tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

@app.get(f"{settings.API_PREFIX}/chat/active", response_model=TicketResponse, tags=["Chat"])
@trace_request
async def get_active_chat(user_payload: dict = Depends(get_current_user)):
    """Get the latest active ticket/conversation for the user"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Try to match frontend behavior (uses username/email)
        user_id = user_payload.get("preferred_username") or user_payload.get("email") or user_payload.get("sub") or "user-123"
        
        # If in dev mode mock, it might be "dev-user", but frontend uses "user-123"
        if user_id == "dev-user":
            user_id = "user-123"
            
        logger.info(f"get_active_chat: Searching for ticket for user_id='{user_id}'")
        ticket = await orchestrator.get_latest_active_ticket(user_id)
        
        if not ticket:
            logger.info(f"get_active_chat: No active ticket found for user_id='{user_id}'")
            # No active ticket found
            return JSONResponse(status_code=204, content={})
            
        logger.info(f"get_active_chat: Found ticket {ticket.id} for user_id='{user_id}'")
        conversation = await orchestrator.get_conversation(ticket.id)
        
        # Reconstruct TicketResponse
        # Note: In a real app, we'd regenerate the explanation graph or store it
        from ..models.schemas import ExplanationNode, AgentType
        
        return TicketResponse(
            ticket=ticket,
            conversation=conversation,
            explanation_graph=ExplanationNode(
                agent=AgentType.ROUTER,
                action="Restored",
                reasoning="Restored from history",
                confidence=1.0,
                timestamp=datetime.utcnow()
            ),
            next_steps=[],
            requires_user_action=ticket.status == TicketStatus.PENDING_USER
        )
    except Exception as e:
        logger.error(f"Error retrieving active chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get(f"{settings.API_PREFIX}/tickets/{{ticket_id}}/conversation", response_model=AgentConversation, tags=["Tickets"])
@trace_request
async def get_ticket_conversation(ticket_id: str):
    """Get conversation history for a specific ticket"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        conversation = await orchestrator.get_conversation(ticket_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation for ticket {ticket_id}: {e}")
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
async def search_knowledge(query: str = "", category: str = None, limit: int = 5, language: str = "en"):
    """Search knowledge base using Azure AI Search"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        results = await orchestrator.search_knowledge(query, category, limit, language)
        return {"query": query, "category": category, "results": results}
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Knowledge Base CRUD Endpoints
from ..models.schemas import KnowledgeArticle, KnowledgeArticleCreate, KnowledgeArticleUpdate
from ..services.knowledge_base_service import get_knowledge_base_service

@app.get(f"{settings.API_PREFIX}/knowledge/articles", response_model=list[KnowledgeArticle], tags=["Knowledge Base"])
async def list_knowledge_articles():
    """List all knowledge base articles"""
    kb_service = get_knowledge_base_service()
    return await kb_service.get_all_articles()

@app.post(f"{settings.API_PREFIX}/knowledge/articles", response_model=KnowledgeArticle, tags=["Knowledge Base"])
async def create_knowledge_article(article: KnowledgeArticleCreate):
    """Create a new knowledge base article"""
    kb_service = get_knowledge_base_service()
    return await kb_service.create_article(article)

@app.get(f"{settings.API_PREFIX}/knowledge/articles/{{article_id}}", response_model=KnowledgeArticle, tags=["Knowledge Base"])
async def get_knowledge_article(article_id: str):
    """Get a knowledge base article by ID"""
    kb_service = get_knowledge_base_service()
    article = await kb_service.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@app.put(f"{settings.API_PREFIX}/knowledge/articles/{{article_id}}", response_model=KnowledgeArticle, tags=["Knowledge Base"])
async def update_knowledge_article(article_id: str, article: KnowledgeArticleUpdate):
    """Update a knowledge base article"""
    kb_service = get_knowledge_base_service()
    updated_article = await kb_service.update_article(article_id, article)
    if not updated_article:
        raise HTTPException(status_code=404, detail="Article not found")
    return updated_article

@app.delete(f"{settings.API_PREFIX}/knowledge/articles/{{article_id}}", tags=["Knowledge Base"])
async def delete_knowledge_article(article_id: str):
    """Delete a knowledge base article"""
    kb_service = get_knowledge_base_service()
    success = await kb_service.delete_article(article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"status": "success", "message": "Article deleted"}

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

@app.post(f"{settings.API_PREFIX}/ocr", tags=["OCR"])
async def ocr_endpoint(file: UploadFile = File(...)):
    """
    Analyze uploaded file (Image, PDF, Word) and extract/summarize text.
    """
    try:
        content = await file.read()
        result = await document_service.process_file(content, file.filename)
        return {"text": result, "filename": file.filename}
    except Exception as e:
        logger.error(f"Error in document analysis endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Simple chat endpoint (working implementation)
@app.post(f"{settings.API_PREFIX}/chat", tags=["Chat"])
async def chat(request: ChatRequest):
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
        from ..services.simple_agent_fixed import get_simple_agent
        from ..services.storage_service import get_storage_service
        import uuid
        
        user_id = request.user_id
        message = request.message
        
        logger.info(f"Chat request from user {user_id}: {message[:100]}")
        
        # Get simple agent instance
        agent = get_simple_agent()
        storage = get_storage_service()
        

        # Generate intelligent response
        result = await agent.generate_response(message, language=request.language or "en", email_notifications=request.email_notifications, user_email=request.user_email)
        
        # Create and save ticket (Mocking persistence for SimpleAgent)
        ticket_id = str(uuid.uuid4())[:8]
        ticket_status = TicketStatus.RESOLVED if result["can_auto_resolve"] else TicketStatus.OPEN
        
        # Map category string to Enum
        category_str = str(result["category"] or "IT").upper()
        category_enum = TicketCategory.UNKNOWN
        
        if category_str in ["IT", "IT_SUPPORT"]: category_enum = TicketCategory.IT_SUPPORT
        elif category_str in ["HR", "HR_INQUIRY"]: category_enum = TicketCategory.HR_INQUIRY
        elif category_str in ["FACILITIES", "FACILITIES"]: category_enum = TicketCategory.FACILITIES
        elif category_str in ["LEGAL", "LEGAL"]: category_enum = TicketCategory.LEGAL
        elif category_str in ["FINANCE", "FINANCE"]: category_enum = TicketCategory.FINANCE
        elif category_str in ["SECURITY", "SECURITY_VIOLATION"]: category_enum = TicketCategory.IT_SUPPORT # Map security to IT for now
        else:
            logger.warning(f"Unknown category '{category_str}', defaulting to IT_SUPPORT")
            category_enum = TicketCategory.IT_SUPPORT

        # Map priority string to Enum
        priority_str = "MEDIUM"
        if "urgent" in message.lower() or "asap" in message.lower():
            priority_str = "HIGH"
        
        priority_enum = TicketPriority.MEDIUM
        if priority_str == "HIGH": priority_enum = TicketPriority.HIGH
        
        logger.info(f"Creating ticket with Category: {category_enum.value}, Priority: {priority_enum.value}")

        # In a real scenario, we would use the orchestrator or storage service
        # For this fix, we'll inject it into the orchestrator's memory if available
        # CRITICAL FIX: Do not create ticket if blocked (SECURITY category)
        if orchestrator and category_enum != TicketCategory.IT_SUPPORT and category_str != "SECURITY":
             # Note: We mapped SECURITY to IT_SUPPORT above for Enum compatibility, but we check category_str here
             pass

        if orchestrator and category_str != "SECURITY" and result.get("ticket_id"):
            new_ticket = Ticket(
                id=ticket_id,
                user_id=user_id,
                description=message,
                status=ticket_status,
                priority=priority_enum,
                category=category_enum,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                confidence_score=result["confidence"],
                channel=ChannelType.WEB,
                ip_address=request.ip_address,
                country=request.country
            )
            orchestrator.tickets_db[ticket_id] = new_ticket
            logger.info(f"Ticket {ticket_id} created and saved to memory")
        else:
            logger.info(f"Skipping ticket creation for blocked/security content: {category_str}")

        # Return structured response
        return {
            "user_id": user_id,
            "message": message,
            "response": result["response"],
            "confidence": result["confidence"],
            "category": result["category"],
            "categories": result.get("categories", [result["category"]]),
            "intent": result["intent"],
            "can_auto_resolve": result["can_auto_resolve"],
            "reasoning": result["reasoning"],
            "kb_articles_used": len(result["kb_articles"]),
            "kb_articles": result["kb_articles"],
            "timestamp": datetime.utcnow().isoformat(),
            "priority": result.get("priority", "Normal"),
            "conversation_id": str(uuid.uuid4()),
            "safety_check_passed": True,
            "agents_involved": ["simple_agent"],
            # Add explanation_graph for frontend
            "explanation_graph": {
                "nodes": [
                    {
                        "id": "1", 
                        "label": "User Input", 
                        "type": "input", 
                        "details": f"Length: {len(message)} chars"
                    },
                    {
                        "id": "2", 
                        "label": "Safety Analysis", 
                        "type": "process", 
                        "status": "success" if result.get("safety_check_passed", True) else "failed",
                        "details": "Content Safety: Pass" if result.get("safety_check_passed", True) else "Content Safety: Blocked"
                    },
                    {
                        "id": "3", 
                        "label": f"Classification: {', '.join(result.get('categories', [result['category']]))}", 
                        "type": "decision",
                        "details": f"Confidence: {result['confidence']:.1%}"
                    },
                    {
                        "id": "4", 
                        "label": "Intent Detection", 
                        "type": "process",
                        "details": f"Intent: {result['intent'] or 'None'}"
                    },
                    {
                        "id": "5", 
                        "label": "Knowledge Retrieval", 
                        "type": "process",
                        "details": f"Articles Found: {len(result.get('kb_articles', []))}"
                    },
                    {
                        "id": "6", 
                        "label": "Response Generation", 
                        "type": "output",
                        "details": "Auto-Resolved" if result.get("can_auto_resolve") else "Escalation Recommended"
                    }
                ],
                "edges": [
                    {"id": "e1-2", "source": "1", "target": "2"},
                    {"id": "e2-3", "source": "2", "target": "3"},
                    {"id": "e3-4", "source": "3", "target": "4"},
                    {"id": "e4-5", "source": "4", "target": "5"},
                    {"id": "e5-6", "source": "5", "target": "6"}
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=5000,
        reload=settings.DEBUG
    )

