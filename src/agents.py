import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.state import (
    AgentState,
    TicketCategory,
    KBSearchResult,
    ResolutionDraft,
    QualityCheckResult,
    EscalationDecision,
)
from src.rag import search_kb

load_dotenv()

_llm: ChatOpenAI | None = None


def get_llm(temperature: float = 0.2) -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    return _llm


# ─────────────────────────────────────────────
# GUARDRAIL NODE
# ─────────────────────────────────────────────

def guardrail_node(state: AgentState) -> AgentState:
    """Validates the incoming ticket before processing begins."""
    ticket = state.ticket
    issues = []

    if not ticket.body or len(ticket.body.strip()) < 15:
        issues.append("Ticket body is too short or empty.")
    if not ticket.customer_email or "@" not in ticket.customer_email:
        issues.append("Invalid or missing customer email.")
    if not ticket.subject or len(ticket.subject.strip()) < 3:
        issues.append("Subject line is missing or too short.")

    off_topic_keywords = ["pizza", "weather", "sports", "movie", "recipe", "joke"]
    body_lower = ticket.body.lower()
    if any(kw in body_lower for kw in off_topic_keywords):
        issues.append("Ticket appears to be off-topic and unrelated to AutoVoice AI services.")

    if issues:
        trace = state.agent_trace + [f"[GUARDRAIL] Validation failed: {'; '.join(issues)}"]
        return state.model_copy(
            update={"guardrail_triggered": "; ".join(issues), "agent_trace": trace}
        )

    trace = state.agent_trace + ["[GUARDRAIL] Ticket passed validation."]
    return state.model_copy(update={"agent_trace": trace})


# ─────────────────────────────────────────────
# TRIAGE AGENT
# ─────────────────────────────────────────────

def triage_agent(state: AgentState) -> AgentState:
    """Classifies the ticket by category, urgency, and customer sentiment."""
    llm = get_llm(temperature=0.1)
    structured = llm.with_structured_output(TicketCategory)

    prompt = f"""You are the Triage Agent for AutoVoice AI — a B2B SaaS platform providing AI voice and SMS agents for US car dealerships.

Analyze the following support ticket and classify it.

Categories:
- call_quality: AI misunderstanding callers, dropped calls, wrong responses, audio issues, slow responses
- crm_integration: DealerSocket, VinSolutions, CDK, Elead, Dealertrack sync issues, API errors, duplicate leads
- billing: invoices, charges, payment failures, plan upgrades/downgrades, overages, refunds
- onboarding_configuration: new setup, script builder, phone numbers, go-live issues, settings
- compliance_legal: TCPA, DNC, recording consent, legal threats, opt-out issues
- other: anything that doesn't fit above categories

Urgency levels:
- critical: legal threat, service completely down, data breach, payment failure affecting service
- high: major functionality broken, angry customer threatening to cancel, compliance risk
- medium: functionality degraded, billing confusion, integration not working
- low: general questions, how-to requests, minor issues

Sentiment:
- positive: polite, satisfied, just needs help
- neutral: matter-of-fact, no strong emotion
- frustrated: clearly annoyed but not aggressive
- angry: aggressive, threatening, using harsh language

---
Ticket Subject: {state.ticket.subject}
Ticket Body: {state.ticket.body}
Dealership: {state.ticket.dealership_name}
Plan: {state.ticket.account_plan or "Unknown"}
---"""

    result: TicketCategory = structured.invoke([HumanMessage(content=prompt)])
    trace = state.agent_trace + [
        f"[TRIAGE] Category: {result.category} | Urgency: {result.urgency} | Sentiment: {result.sentiment} | Confidence: {result.confidence:.0%}"
    ]
    return state.model_copy(update={"triage": result, "agent_trace": trace})


# ─────────────────────────────────────────────
# ESCALATION AGENT
# ─────────────────────────────────────────────

def escalation_agent(state: AgentState) -> AgentState:
    """Determines if the ticket needs human escalation and which team should handle it."""
    llm = get_llm(temperature=0.1)
    structured = llm.with_structured_output(EscalationDecision)

    triage = state.triage
    prompt = f"""You are the Escalation Agent for AutoVoice AI support.

Based on the ticket details and triage results, decide whether this ticket requires human escalation.

Escalate if ANY of the following are true:
1. Urgency is "critical" or "high"
2. Category is "compliance_legal"
3. Customer sentiment is "angry"
4. Customer mentions "lawyer", "lawsuit", "TCPA violation", "sue", "attorney", "complaint", "BBB", "FTC"
5. The issue involves a data breach or security concern
6. The ticket mentions wanting to cancel their account

If escalating, choose the appropriate team:
- tier2_support: complex technical issues beyond self-service
- billing_team: billing disputes, refund requests, payment issues
- compliance_legal: any legal threats, TCPA issues, DNC violations
- engineering: platform outages, data loss, integration bugs

---
Ticket: {state.ticket.subject}
Body: {state.ticket.body}
Category: {triage.category if triage else "unknown"}
Urgency: {triage.urgency if triage else "unknown"}
Sentiment: {triage.sentiment if triage else "unknown"}
---"""

    result: EscalationDecision = structured.invoke([HumanMessage(content=prompt)])
    trace = state.agent_trace + [
        f"[ESCALATION] Escalate: {result.should_escalate} | Team: {result.escalation_team} | Priority: {result.priority} | Reason: {result.reason}"
    ]
    return state.model_copy(update={"escalation": result, "agent_trace": trace})


# ─────────────────────────────────────────────
# KNOWLEDGE AGENT
# ─────────────────────────────────────────────

def knowledge_agent(state: AgentState) -> AgentState:
    """Searches the knowledge base to find relevant information for resolving the ticket."""
    triage = state.triage
    query = f"{state.ticket.subject} {state.ticket.body}"

    category_queries = {
        "call_quality": "call quality issues AI transcription accuracy audio problems",
        "crm_integration": "CRM integration setup DealerSocket VinSolutions CDK sync error",
        "billing": "billing invoice payment plan overage refund",
        "onboarding_configuration": "onboarding setup configuration script builder phone number",
        "compliance_legal": "TCPA compliance DNC call recording consent opt-out",
    }

    if triage and triage.category in category_queries:
        category_hint = category_queries[triage.category]
        query = f"{query} {category_hint}"

    raw_results = search_kb(query, k=4)
    kb_results = [
        KBSearchResult(
            source=r["source"],
            content=r["content"],
            relevance_score=r["relevance_score"],
        )
        for r in raw_results
    ]

    trace = state.agent_trace + [
        f"[KNOWLEDGE] Retrieved {len(kb_results)} KB chunks. Top source: {kb_results[0].source if kb_results else 'none'}"
    ]
    return state.model_copy(update={"kb_results": kb_results, "agent_trace": trace})


# ─────────────────────────────────────────────
# RESOLUTION AGENT
# ─────────────────────────────────────────────

def resolution_agent(state: AgentState) -> AgentState:
    """Drafts a professional, empathetic response to the customer using KB context."""
    llm = get_llm(temperature=0.4)
    structured = llm.with_structured_output(ResolutionDraft)

    kb_context = "\n\n---\n\n".join(
        [f"[{r.source}]\n{r.content}" for r in state.kb_results[:3]]
    ) if state.kb_results else "No specific KB content found — use general product knowledge."

    previous_issues = ""
    if state.quality_check and not state.quality_check.passed:
        previous_issues = f"\n\nPREVIOUS DRAFT ISSUES TO FIX:\n" + "\n".join(
            f"- {issue}" for issue in state.quality_check.issues
        )

    triage = state.triage
    sentiment = triage.sentiment if triage else "neutral"
    category = triage.category if triage else "other"

    tone_map = {
        "angry": "apologetic",
        "frustrated": "empathetic",
        "neutral": "professional",
        "positive": "professional",
    }
    suggested_tone = tone_map.get(sentiment, "professional")

    prompt = f"""You are the Resolution Agent for AutoVoice AI customer support.

Draft a professional, helpful email response to the following support ticket. 
The tone should be {suggested_tone}. Be specific, actionable, and reference the exact steps from the knowledge base.
Do NOT make up features or policies not in the knowledge base.
Sign the email as: "The AutoVoice AI Support Team"

KNOWLEDGE BASE CONTEXT:
{kb_context}

TICKET DETAILS:
Customer Name: {state.ticket.customer_name}
Dealership: {state.ticket.dealership_name}
Subject: {state.ticket.subject}
Body: {state.ticket.body}
Category: {category}
{previous_issues}"""

    result: ResolutionDraft = structured.invoke([HumanMessage(content=prompt)])
    trace = state.agent_trace + [
        f"[RESOLUTION] Draft written. Tone: {result.tone} | Actions suggested: {len(result.suggested_actions)} | Retry #{state.retry_count}"
    ]
    return state.model_copy(
        update={"resolution_draft": result, "agent_trace": trace, "retry_count": state.retry_count + 1}
    )


# ─────────────────────────────────────────────
# QUALITY AGENT
# ─────────────────────────────────────────────

def quality_agent(state: AgentState) -> AgentState:
    """Reviews the drafted response for tone, accuracy, policy compliance, and professionalism."""
    llm = get_llm(temperature=0.1)
    structured = llm.with_structured_output(QualityCheckResult)

    draft = state.resolution_draft

    prompt = f"""You are the Quality Assurance Agent for AutoVoice AI support.

Review the following draft response and check for:
1. Professional and empathetic tone (no condescending or dismissive language)
2. No made-up features, policies, or pricing not grounded in the knowledge base
3. Clear, actionable steps — not vague advice
4. Proper greeting and closing
5. No grammatical errors or unprofessional phrasing
6. Does not promise things we cannot deliver (e.g., "we'll fix it today" without certainty)
7. Complies with AutoVoice AI's policy of not providing legal advice
8. Is complete — actually addresses the customer's problem

If the draft passes all checks, set passed=True and leave issues empty.
If there are issues, set passed=False and list specific issues. Optionally provide a revised_body.

DRAFT SUBJECT: {draft.subject if draft else "N/A"}
DRAFT BODY:
{draft.body if draft else "N/A"}"""

    result: QualityCheckResult = structured.invoke([HumanMessage(content=prompt)])
    trace = state.agent_trace + [
        f"[QUALITY] Check {'PASSED' if result.passed else 'FAILED'}. Issues: {result.issues if result.issues else 'none'}"
    ]
    return state.model_copy(update={"quality_check": result, "agent_trace": trace})
