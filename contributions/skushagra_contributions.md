# Individual Contribution — Kushagra S.

**Project:** AutoVoice AI — Multi-Agent Customer Support System
**Course:** Multi Agent Orchestration [AI/ML]
**Role:** System Architecture and Graph Orchestration

---

## Overview

My responsibility was the overall system architecture and the LangGraph orchestration layer — the backbone that connects all agents, manages shared state, controls routing decisions, and implements the human-in-the-loop checkpoints.

---

## Contributions

### 1. System Architecture and Problem Design

- Defined the overall product concept: an AI-powered support system for a voice/text automation platform serving US car dealerships
- Designed the multi-agent pipeline flow from ticket ingestion to resolution or escalation
- Identified the five distinct agent roles, their responsibilities, and handoff points
- Mapped all branching conditions: normal resolution path, escalation path, guardrail rejection path, and quality retry loop

### 2. State Schema Design (`src/state.py`)

- Designed the full Pydantic state schema used across all agents
- Defined structured output models for every agent: `TicketCategory`, `KBSearchResult`, `ResolutionDraft`, `QualityCheckResult`, `EscalationDecision`, `SupportTicket`
- Ensured all inter-agent handoffs use typed, schema-validated outputs (no untyped dicts)
- Added `agent_trace` field to track the execution history of all nodes for observability
- Added `retry_count`, `guardrail_triggered`, `send_status` fields for routing control

### 3. LangGraph Graph Implementation (`src/graph.py`)

- Built the complete LangGraph `StateGraph` with all 11 nodes wired together
- Implemented all five routing functions:
  - `route_after_guardrail` — reject or continue to triage
  - `route_after_triage` — always routes to escalation check first
  - `route_after_escalation` — direct to human interrupt or knowledge search
  - `route_after_quality` — pass to human review or retry resolution (max 2 retries)
  - `route_after_human_approval` — send response, revise, or escalate
- Implemented two human-in-the-loop interrupt nodes using `interrupt_before` in LangGraph
- Used `MemorySaver` checkpointer to persist state across graph interruptions and resumptions
- Exposed `compile_graph()` function that wires the full graph with checkpointer injection

### 4. Human-in-the-Loop Architecture

- Designed the two HITL checkpoint pattern: one for escalation approval, one for response approval
- Ensured graph state is correctly resumed after human input by using `graph.update_state()` before re-streaming
- Implemented the `human_approved` and `human_feedback` fields in state to carry human decisions downstream
- Verified the retry loop: if a human rejects a draft, the resolution agent re-runs with the feedback attached

### 5. Project Setup and Dependency Management

- Initialised the project repository structure (`src/`, `knowledge_base/`, `evaluation/`, `contributions/`)
- Authored `requirements.txt` with all pinned dependencies
- Created `.env.example` with required environment variables and documentation
- Created `.gitignore` to exclude `.env`, `.venv/`, `.chroma_db/`, and all sensitive or generated files
- Configured `uv` virtual environment (`python3.12`) and resolved import compatibility issues with LangChain 1.3 API changes

---

## Files Owned

| File | Description |
|------|-------------|
| `src/state.py` | Full Pydantic state schema for all agents |
| `src/graph.py` | LangGraph graph, routing functions, HITL interrupts |
| `requirements.txt` | All project dependencies |
| `.env.example` | Environment variable template |
| `.gitignore` | Repository ignore rules |

---

## Design Decisions I Made

- **Why LangGraph over CrewAI:** LangGraph gives explicit control over state, routing, and checkpointing. The HITL pattern requires persisting mid-graph state across Streamlit rerenders, which only LangGraph's checkpointer supports cleanly.
- **Why Pydantic for all outputs:** Untyped dict passing between agents causes silent failures. Structured outputs enforce contracts at each handoff.
- **Why two HITL nodes instead of one:** Escalation and response approval require different context and different downstream paths. Merging them into one node would have made routing logic opaque.
- **Why a retry cap of 2:** Unlimited retries risk infinite loops if the quality agent consistently rejects drafts. Two attempts catch genuine quality issues without hanging the system.
