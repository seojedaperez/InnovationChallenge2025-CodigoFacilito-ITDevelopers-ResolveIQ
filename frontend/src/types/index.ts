export type TicketCategory = 'it_support' | 'hr_inquiry' | 'facilities' | 'legal' | 'finance' | 'unknown';

export type TicketPriority = 'low' | 'medium' | 'high' | 'critical';

export type TicketStatus = 'open' | 'in_progress' | 'pending_user' | 'escalated' | 'resolved' | 'closed';

export type AgentType =
    | 'planner'
    | 'router'
    | 'it_specialist'
    | 'hr_specialist'
    | 'facilities_specialist'
    | 'legal_specialist'
    | 'finance_specialist'
    | 'executor'
    | 'explainer'
    | 'safety'
    | 'escalation'
    | 'USER';

export interface Ticket {
    id: string;
    user_id: string;
    description: string;
    channel: string;
    priority: TicketPriority;
    status: TicketStatus;
    category: TicketCategory;
    created_at: string;
    resolved_at?: string;
    confidence_score?: number;
    assigned_agent?: string;
    resolution?: string;
    escalation_reason?: string;
    ip_address?: string;
    country?: string;
}

export interface AgentMessage {
    agent_type: AgentType;
    content: string;
    confidence: number;
    reasoning?: string;
    actions_taken?: string[];
    timestamp: string;
}

export interface AgentConversation {
    id: string;
    ticket_id: string;
    thread_id: string;
    messages: AgentMessage[];
}

export interface ExplanationNode {
    agent: AgentType;
    action: string;
    reasoning: string;
    confidence: number;
    timestamp: string;
    children?: ExplanationNode[];
}

export interface TicketResponse {
    ticket: Ticket;
    conversation: AgentConversation;
    explanation_graph: ExplanationNode;
    next_steps: string[];
    requires_user_action: boolean;
}
