# Individual Contribution — Archisman

**Project:** AutoVoice AI — Multi-Agent Customer Support System
**Course:** Multi Agent Orchestration [AI/ML]
**Role:** Safety, Tools, UI, and Evaluation

---

## Overview

My responsibility was everything that touches the boundary between the system and the outside world: the guardrails that protect the pipeline, the tools that agents call, the agents that handle escalation and quality control, the Streamlit interface that makes the system demoable, and the evaluation suite that verifies correctness.

---

## Contributions

### 1. Guardrail Node (`src/agents.py` — `guardrail_node`)

- Implemented the first node in the pipeline: a non-LLM, rule-based validation layer
- Rejects tickets that fail any of the following checks before any LLM call is made:
  - Ticket body shorter than 15 characters (empty or trivial messages)
  - Missing or malformed customer email address
  - Subject line missing or too short
  - Off-topic content: detects non-support keywords (`pizza`, `weather`, `sports`, `recipe`, etc.)
- Stores the rejection reason in `guardrail_triggered` field, which routes the graph to a terminal rejection node
- Design rationale: catches obvious invalid inputs cheaply without burning LLM tokens, and prevents prompt injection attempts via ticket body

### 2. Escalation Agent (`src/agents.py` — `escalation_agent`)

- Implemented the Escalation Agent using structured output (`EscalationDecision`)
- Designed the escalation decision prompt with explicit criteria covering: urgency level, customer sentiment, legal language detection (`lawyer`, `TCPA`, `FTC`, `sue`, `attorney`), data breach signals, and cancellation threats
- Maps escalation decisions to the correct specialist team:
  - `compliance_legal` — for TCPA/DNC/legal threats
  - `billing_team` — for payment disputes and refund requests
  - `engineering` — for platform outages and data loss
  - `tier2_support` — for complex technical issues
- Assigns SLA-based priority: `immediate` (1 hr), `urgent` (4 hrs), `normal` (24 hrs)

### 3. Quality Agent (`src/agents.py` — `quality_agent`)

- Implemented the Quality Agent as the last automated check before human review
- Reviews every draft response against eight quality criteria:
  1. Professional and empathetic tone
  2. No fabricated features, policies, or pricing
  3. Clear, actionable steps (not vague advice)
  4. Proper greeting and sign-off
  5. No grammatical errors or unprofessional phrasing
  6. No undeliverable promises
  7. Compliance with the policy of not providing legal advice
  8. Completeness — actually addresses the customer's stated problem
- Returns `passed: True/False` with a list of specific issues and optionally a `revised_body`
- Feeds issues back to the Resolution Agent on retry

### 4. Tools (`src/tools.py`)

Implemented all four LangChain tools available to the agent system:

| Tool | Purpose |
|------|---------|
| `search_knowledge_base` | Wraps `search_kb()` as a LangChain tool; formats results with source attribution |
| `lookup_account` | Returns mock account data (plan, usage, payment status, CRM) by account ID |
| `send_response_email` | Simulates email delivery; returns confirmation ID and timestamp |
| `flag_compliance_issue` | Creates a compliance flag record and notifies the compliance team (mock) |
| `create_escalation_ticket` | Creates an internal escalation ticket with team assignment and SLA |

- All tools use `@tool` decorator for LangChain compatibility
- `send_response_email` and `flag_compliance_issue` are intentionally gated behind human approval in the graph — they are high-impact external actions
- `lookup_account` contains realistic mock data for three dealership accounts with different plan types, usage levels, and payment statuses

### 5. Streamlit UI (`app.py`)

Built the complete demo interface with the following structure:

**Sidebar:**
- Six pre-loaded demo scenarios covering all ticket categories
- Each scenario auto-fills the form and resets pipeline state correctly
- "New Ticket" button performs a clean session reset

**Left column — Ticket:**
- Before submission: full ticket form with all fields
- After submission: read-only ticket summary card (ID badge, subject, contact details, message)

**Right column — Agent Pipeline:**
- Six numbered step rows that fill in progressively as each agent completes
- Each step shows: agent name, output summary, and a status tag (Passed / Retrieved / Pending / etc.)
- Pending steps remain visible as greyed-out rows so the full pipeline is always legible
- Human Review panel appears inline for escalation approval and response approval
- Result banners for all three terminal states: sent, escalated, rejected
- Full email shown in an email-client-style widget after approval
- Agent trace collapsed in an expander — available but not cluttering the view

**Key UI decisions:**
- No emojis, no gradients — plain text labels and flat colour tags only
- Step circles: grey (pending), black (active), green (done), red (error)
- Two-column layout is fixed at `[4, 6]` ratio with `gap="large"` for breathing room

### 6. Evaluation Suite (`evaluation/test_cases.py`)

Wrote the full evaluation framework with eight test cases covering every important scenario:

| ID | Scenario | What it validates |
|----|----------|-------------------|
| TC-001 | Normal CRM sync issue | Correct category, no false escalation, KB retrieval |
| TC-002 | TCPA legal threat | Escalation to compliance_legal team, critical urgency |
| TC-003 | Billing overage confusion | Billing category, KB retrieval, no escalation |
| TC-004 | AI quality issue — angry customer | Escalation triggered, call_quality category |
| TC-005 | Onboarding script question | Low urgency, onboarding category, KB retrieval |
| TC-006 | Off-topic ticket | Guardrail triggered, pipeline does not run |
| TC-007 | Empty/invalid ticket | Guardrail triggered on short body + bad email |
| TC-008 | Cancellation threat | Critical urgency, escalation triggered |

- Each test case defines expected category, urgency ceiling, escalation decision, escalation team, and KB hit
- Runner streams graph output, extracts structured results, and checks each expectation independently
- Prints a formatted summary table using `rich` with per-test pass/fail counts
- Designed to be run headlessly: `python -m evaluation.test_cases`

---

## Files Owned

| File | Description |
|------|-------------|
| `app.py` | Complete Streamlit demo interface |
| `src/tools.py` | All four LangChain tools |
| `src/agents.py` (Guardrail, Escalation, Quality) | Three agent implementations |
| `evaluation/test_cases.py` | Full evaluation suite with 8 test cases |

---

## Design Decisions I Made

- **Why rule-based guardrail instead of LLM-based:** An LLM guardrail adds latency and cost to every ticket, including clearly invalid ones. A fast rule-based check filters 90% of junk before touching the LLM budget.
- **Why 8 test cases instead of the minimum 5:** The rubric requires 5 but meaningful evaluation needs edge cases. TC-006 and TC-007 specifically test the guardrail layer which would be invisible in a standard happy-path test suite.
- **Why the Quality Agent uses 8 specific criteria instead of a vague "is this good?":** A vague quality prompt returns inconsistent results. Explicit criteria make the agent's judgement reproducible and debuggable.
- **Why mock tools instead of real APIs:** Real email and CRM APIs introduce external dependencies that fail during demos. Mock tools with realistic response shapes prove the system works end-to-end without network risk during a live presentation.
