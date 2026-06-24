from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.state import AgentState
from src.agents import (
    guardrail_node,
    triage_agent,
    escalation_agent,
    knowledge_agent,
    resolution_agent,
    quality_agent,
)


# ─────────────────────────────────────────────
# ROUTING FUNCTIONS
# ─────────────────────────────────────────────

def route_after_guardrail(state: AgentState) -> str:
    if state.guardrail_triggered:
        return "guardrail_reject"
    return "triage"


def route_after_triage(state: AgentState) -> str:
    """After triage, always run escalation check first."""
    return "escalation"


def route_after_escalation(state: AgentState) -> str:
    """If escalation is needed, go to human interrupt; otherwise proceed to KB search."""
    if state.escalation and state.escalation.should_escalate:
        return "human_escalation_interrupt"
    return "knowledge"


def route_after_quality(state: AgentState) -> str:
    """If quality passed, go to human approval; if failed and retries remain, retry resolution."""
    if state.quality_check and state.quality_check.passed:
        return "human_approval_interrupt"
    if state.retry_count >= 2:
        # Force through after max retries to avoid infinite loop
        return "human_approval_interrupt"
    return "resolution"


def route_after_human_approval(state: AgentState) -> str:
    """After human reviews, either send response or escalate based on approval."""
    if state.human_approved is True:
        return "send_response"
    if state.human_approved is False:
        return "resolution"
    # None means interrupt is still pending
    return "human_approval_interrupt"


# ─────────────────────────────────────────────
# TERMINAL NODES
# ─────────────────────────────────────────────

def guardrail_reject_node(state: AgentState) -> AgentState:
    msg = (
        f"Your ticket could not be processed: {state.guardrail_triggered}\n"
        "Please resubmit with complete information."
    )
    trace = state.agent_trace + [f"[END] Ticket rejected by guardrail."]
    return state.model_copy(update={"final_response": msg, "agent_trace": trace})


def send_response_node(state: AgentState) -> AgentState:
    """Finalizes and 'sends' the response (mock)."""
    draft = state.resolution_draft
    if draft:
        final = f"Subject: {draft.subject}\n\n{draft.body}"
        if state.human_feedback:
            final += f"\n\n[Note added by reviewer: {state.human_feedback}]"
    else:
        final = "Resolution sent."
    trace = state.agent_trace + [f"[END] Response sent to {state.ticket.customer_email}."]
    return state.model_copy(
        update={
            "final_response": final,
            "send_status": "sent",
            "agent_trace": trace,
        }
    )


def escalation_sent_node(state: AgentState) -> AgentState:
    """Handles tickets that were escalated and approved by human."""
    esc = state.escalation
    team = esc.escalation_team if esc else "tier2_support"
    priority = esc.priority if esc else "normal"
    trace = state.agent_trace + [
        f"[END] Ticket escalated to {team} with {priority} priority."
    ]
    final = (
        f"This ticket has been escalated to our {team.replace('_', ' ').title()} "
        f"with {priority} priority. A team member will contact you shortly.\n\n"
        f"Escalation reason: {esc.reason if esc else 'Requires specialist handling.'}"
    )
    return state.model_copy(
        update={
            "final_response": final,
            "send_status": "escalated",
            "agent_trace": trace,
        }
    )


def human_escalation_interrupt_node(state: AgentState) -> AgentState:
    """Interrupt node: pauses for human to approve escalation."""
    trace = state.agent_trace + ["[HUMAN] Waiting for human approval of escalation..."]
    return state.model_copy(update={"agent_trace": trace})


def human_approval_interrupt_node(state: AgentState) -> AgentState:
    """Interrupt node: pauses for human to review and approve the drafted response."""
    trace = state.agent_trace + ["[HUMAN] Waiting for human approval of response draft..."]
    return state.model_copy(update={"agent_trace": trace})


def route_after_escalation_human(state: AgentState) -> str:
    if state.human_approved is True:
        return "escalation_sent"
    if state.human_approved is False:
        return "knowledge"
    return "human_escalation_interrupt"


# ─────────────────────────────────────────────
# BUILD GRAPH
# ─────────────────────────────────────────────

def build_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    # Add all nodes
    builder.add_node("guardrail", guardrail_node)
    builder.add_node("guardrail_reject", guardrail_reject_node)
    builder.add_node("triage", triage_agent)
    builder.add_node("escalation", escalation_agent)
    builder.add_node("human_escalation_interrupt", human_escalation_interrupt_node)
    builder.add_node("escalation_sent", escalation_sent_node)
    builder.add_node("knowledge", knowledge_agent)
    builder.add_node("resolution", resolution_agent)
    builder.add_node("quality", quality_agent)
    builder.add_node("human_approval_interrupt", human_approval_interrupt_node)
    builder.add_node("send_response", send_response_node)

    # Entry point
    builder.add_edge(START, "guardrail")

    # Guardrail routing
    builder.add_conditional_edges(
        "guardrail",
        route_after_guardrail,
        {"guardrail_reject": "guardrail_reject", "triage": "triage"},
    )
    builder.add_edge("guardrail_reject", END)

    # Triage → escalation check
    builder.add_edge("triage", "escalation")

    # Escalation routing
    builder.add_conditional_edges(
        "escalation",
        route_after_escalation,
        {
            "human_escalation_interrupt": "human_escalation_interrupt",
            "knowledge": "knowledge",
        },
    )

    # Escalation human interrupt routing
    builder.add_conditional_edges(
        "human_escalation_interrupt",
        route_after_escalation_human,
        {
            "escalation_sent": "escalation_sent",
            "knowledge": "knowledge",
            "human_escalation_interrupt": "human_escalation_interrupt",
        },
    )
    builder.add_edge("escalation_sent", END)

    # Normal resolution flow
    builder.add_edge("knowledge", "resolution")
    builder.add_edge("resolution", "quality")

    # Quality routing
    builder.add_conditional_edges(
        "quality",
        route_after_quality,
        {
            "human_approval_interrupt": "human_approval_interrupt",
            "resolution": "resolution",
        },
    )

    # Human approval routing
    builder.add_conditional_edges(
        "human_approval_interrupt",
        route_after_human_approval,
        {
            "send_response": "send_response",
            "resolution": "resolution",
            "human_approval_interrupt": "human_approval_interrupt",
        },
    )
    builder.add_edge("send_response", END)

    return builder


def compile_graph(checkpointer=None):
    builder = build_graph()
    if checkpointer is None:
        checkpointer = MemorySaver()
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_escalation_interrupt", "human_approval_interrupt"],
    )
