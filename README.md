# AutoVoice AI — Multi-Agent Customer Support System

A multi-agent AI system built with LangGraph that handles customer support tickets end-to-end for an AI voice and text automation platform serving US car dealerships. Built as a capstone project for the Multi Agent Orchestration course.

---

## What it does

AutoVoice AI receives support tickets from dealership customers, routes them through a pipeline of specialized agents, retrieves relevant documentation via RAG, drafts a resolution, checks quality, and requires human approval before sending any response or escalating any ticket.

---

## Architecture

```
Ticket Input
    └── Guardrail          (validate ticket, reject off-topic/invalid)
         └── Triage Agent  (classify category, urgency, sentiment)
              └── Escalation Agent
                    ├── [High urgency / Legal] ──> Human Approval ──> Escalate to specialist team
                    └── [Normal] ──> Knowledge Agent (RAG search)
                                          └── Resolution Agent (draft response)
                                                └── Quality Agent (review draft)
                                                      └── Human Approval
                                                            ├── Approved ──> Send Email
                                                            └── Rejected ──> Resolution Agent (retry)
```

### Agents

| Agent | Role |
|-------|------|
| Guardrail | Rule-based validation before any LLM call |
| Triage | Classifies category, urgency, sentiment, confidence |
| Escalation | Decides if ticket needs a specialist team |
| Knowledge | RAG search over product documentation |
| Resolution | Drafts the customer response |
| Quality | Reviews draft against eight quality criteria |
| Human-in-the-Loop | Required before sending email or escalating |

### Tools

- `search_knowledge_base` — semantic search over ChromaDB vector store
- `lookup_account` — fetch dealership account details
- `send_response_email` — deliver the approved response
- `flag_compliance_issue` — notify compliance team on legal/TCPA issues
- `create_escalation_ticket` — assign ticket to specialist team with SLA

---

## Tech Stack

- **Orchestration:** LangGraph 1.2 with MemorySaver checkpointing
- **LLM:** GPT-4o-mini via LangChain OpenAI
- **RAG:** ChromaDB + text-embedding-3-small
- **UI:** Streamlit
- **Observability:** LangSmith tracing
- **Runtime:** Python 3.12, uv

---

## Project Structure

```
.
├── app.py                          # Streamlit demo UI
├── src/
│   ├── state.py                    # Pydantic state schema
│   ├── graph.py                    # LangGraph graph and routing
│   ├── agents.py                   # All agent implementations
│   ├── rag.py                      # RAG pipeline and ChromaDB
│   └── tools.py                    # LangChain tools
├── knowledge_base/                 # Product documentation (6 docs)
├── evaluation/
│   └── test_cases.py               # 8 evaluation test cases
├── contributions/                  # Individual contribution docs
├── requirements.txt
└── .env.example
```

---

## Setup

**1. Clone and create virtual environment**

```bash
git clone https://github.com/skushagra-sst/multi-agent-capstone.git
cd multi-agent-capstone
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

**2. Configure environment**

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langsmith_api_key_here   # optional
LANGCHAIN_TRACING_V2=true                        # optional
LANGCHAIN_PROJECT=autovoice-support-agent        # optional
```

**3. Run the app**

```bash
streamlit run app.py
```

**4. Run evaluation**

```bash
python -m evaluation.test_cases
```

---

## Demo Scenarios

The sidebar includes six pre-loaded scenarios that cover every pipeline branch:

| Scenario | Pipeline path |
|----------|--------------|
| CRM Sync Issue | Normal resolution via KB |
| AI Quality — Urgent | Escalation due to high urgency and angry sentiment |
| Billing Confusion | Normal resolution via KB |
| TCPA Legal Threat | Immediate escalation to compliance team |
| Guardrail Test | Rejected before entering pipeline |
| Onboarding Help | Normal resolution via KB |

---

## Evaluation

Eight test cases verify the full pipeline:

| ID | Test | Validates |
|----|------|-----------|
| TC-001 | CRM sync issue | Correct category, KB retrieval, no false escalation |
| TC-002 | TCPA legal threat | Escalation to compliance team, critical urgency |
| TC-003 | Billing overage | Billing category, KB hit |
| TC-004 | AI quality — angry | Escalation triggered, call_quality category |
| TC-005 | Onboarding question | Low urgency, KB retrieval |
| TC-006 | Off-topic ticket | Guardrail rejects before pipeline runs |
| TC-007 | Empty/invalid ticket | Guardrail rejects on bad email and short body |
| TC-008 | Cancellation threat | Critical urgency, escalation triggered |

---

## Team

| Name | GitHub | Role |
|------|--------|------|
| Kushagra S. | [@skushagra](https://github.com/skushagra) | Architecture, state schema, LangGraph orchestration |
| Paramjeet | [@kauxp](https://github.com/kauxp) | Agents, RAG pipeline, knowledge base |
| Archisman | [@Om-Midya](https://github.com/Om-Midya) | Guardrails, tools, Streamlit UI, evaluation |
