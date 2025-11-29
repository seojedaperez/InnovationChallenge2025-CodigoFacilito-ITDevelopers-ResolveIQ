from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class TicketCategory(str, Enum):
    IT_SUPPORT = "it_support"
    HR_INQUIRY = "hr_inquiry"
    FACILITIES = "facilities"
    LEGAL = "legal"
    FINANCE = "finance"
    MULTI = "multi"
    UNKNOWN = "unknown"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_USER = "pending_user"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AgentType(str, Enum):
    PLANNER = "planner"
    ROUTER = "router"
    IT_SPECIALIST = "it_specialist"
    HR_SPECIALIST = "hr_specialist"
    FACILITIES_SPECIALIST = "facilities_specialist"
    LEGAL_SPECIALIST = "legal_specialist"
    FINANCE_SPECIALIST = "finance_specialist"
    EXECUTOR = "executor"
    EXPLAINER = "explainer"
    SAFETY = "safety"
    SAFETY_EVALUATOR = "safety_evaluator"
    ESCALATION = "escalation"


class ChannelType(str, Enum):
    WEB = "web"
    TEAMS = "teams"
    VOICE = "voice"
    API = "api"


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    email: str
    name: str
    department: Optional[str] = None
    role: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TicketCreate(BaseModel):
    user_id: str
    description: str
    channel: ChannelType = ChannelType.WEB
    priority: TicketPriority = TicketPriority.MEDIUM
    metadata: Optional[Dict[str, Any]] = None


class Ticket(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    description: str
    category: TicketCategory = TicketCategory.UNKNOWN
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    channel: ChannelType = ChannelType.WEB
    assigned_agent: Optional[str] = None
    confidence_score: Optional[float] = None
    resolution: Optional[str] = None
    escalation_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentMessage(BaseModel):
    agent_type: AgentType
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    actions_taken: List[str] = Field(default_factory=list)


class AgentConversation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    ticket_id: str
    thread_id: str
    messages: List[AgentMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConfidenceScore(BaseModel):
    ticket_id: str
    overall_confidence: float
    category_confidence: float
    resolution_confidence: float
    model_version: str
    features_used: List[str]
    explanation: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(BaseModel):
    id: str
    ticket_id: str
    user_id: str
    agent_type: Optional[AgentType] = None
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ContentSafetyResult(BaseModel):
    is_safe: bool
    hate_score: float = 0.0
    self_harm_score: float = 0.0
    sexual_score: float = 0.0
    violence_score: float = 0.0
    jailbreak_detected: bool = False
    pii_detected: bool = False
    blocked_reason: Optional[str] = None


class KnowledgeArticle(BaseModel):
    id: str
    title: str
    content: str
    category: TicketCategory
    tags: List[str] = Field(default_factory=list)
    source: str
    relevance_score: Optional[float] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class Runbook(BaseModel):
    id: str
    name: str
    description: str
    category: TicketCategory
    power_automate_flow_id: Optional[str] = None
    required_permissions: List[str] = Field(default_factory=list)
    risk_level: Literal["low", "medium", "high"] = "low"
    auto_executable: bool = True
    parameters: Dict[str, Any] = Field(default_factory=dict)


class Escalation(BaseModel):
    id: str
    ticket_id: str
    reason: str
    confidence_score: float
    agent_recommendation: str
    escalated_to: Optional[str] = None
    teams_adaptive_card_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


class Feedback(BaseModel):
    id: str
    ticket_id: str
    user_id: str
    rating: int = Field(ge=1, le=5)
    was_helpful: bool
    resolution_accurate: bool
    comments: Optional[str] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


class ExplanationNode(BaseModel):
    agent: AgentType
    action: str
    reasoning: str
    confidence: float
    timestamp: datetime
    children: List['ExplanationNode'] = Field(default_factory=list)


class TicketResponse(BaseModel):
    ticket: Ticket
    conversation: AgentConversation
    explanation_graph: ExplanationNode
    next_steps: List[str]
    requires_user_action: bool = False


class HealthCheck(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, str] = Field(default_factory=dict)


class MetricsResponse(BaseModel):
    total_tickets: int
    resolved_tickets: int
    escalated_tickets: int
    average_resolution_time: float
    average_confidence_score: float
    tickets_by_category: Dict[str, int]
    tickets_by_channel: Dict[str, int]
    period_start: datetime
    period_end: datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    user_id: str = Field(..., description="User identifier")
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context information")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    conversation_id: str
    ticket_id: Optional[str] = None
    user_id: str
    message: str
    response: str
    confidence: float
    category: str
    intent: Optional[str] = None
    can_auto_resolve: bool
    reasoning: str
    kb_articles_used: int
    safety_check_passed: bool
    agents_involved: List[str]
    timestamp: datetime
