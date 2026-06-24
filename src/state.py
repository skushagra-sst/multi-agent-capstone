from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


class TicketCategory(BaseModel):
    category: Literal[
        "call_quality",
        "crm_integration",
        "billing",
        "onboarding_configuration",
        "compliance_legal",
        "other",
    ]
    urgency: Literal["low", "medium", "high", "critical"]
    sentiment: Literal["positive", "neutral", "frustrated", "angry"]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


class KBSearchResult(BaseModel):
    source: str
    content: str
    relevance_score: float


class ResolutionDraft(BaseModel):
    subject: str
    body: str
    tone: Literal["empathetic", "professional", "apologetic", "informational"]
    suggested_actions: list[str]


class QualityCheckResult(BaseModel):
    passed: bool
    issues: list[str]
    revised_body: Optional[str] = None


class EscalationDecision(BaseModel):
    should_escalate: bool
    reason: str
    escalation_team: Optional[Literal["tier2_support", "billing_team", "compliance_legal", "engineering"]] = None
    priority: Optional[Literal["normal", "urgent", "immediate"]] = None


class SupportTicket(BaseModel):
    ticket_id: str
    customer_name: str
    customer_email: str
    dealership_name: str
    subject: str
    body: str
    account_plan: Optional[str] = None


class AgentState(BaseModel):
    ticket: SupportTicket
    triage: Optional[TicketCategory] = None
    kb_results: list[KBSearchResult] = []
    resolution_draft: Optional[ResolutionDraft] = None
    quality_check: Optional[QualityCheckResult] = None
    escalation: Optional[EscalationDecision] = None
    human_approved: Optional[bool] = None
    human_feedback: Optional[str] = None
    final_response: Optional[str] = None
    agent_trace: list[str] = []
    retry_count: int = 0
    guardrail_triggered: Optional[str] = None
    send_status: Optional[str] = None
