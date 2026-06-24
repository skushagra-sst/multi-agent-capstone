# Individual Contribution — Paramjeet

**Project:** AutoVoice AI — Multi-Agent Customer Support System
**Course:** Multi Agent Orchestration [AI/ML]
**Role:** Agent Development and RAG Pipeline

---

## Overview

My responsibility was designing and implementing the core intelligence layer of the system — the agents that actually understand the ticket and produce a resolution, and the RAG pipeline that grounds those resolutions in accurate product knowledge. I also authored the entire knowledge base.

---

## Contributions

### 1. Knowledge Base Authoring (`knowledge_base/`)

Wrote all six product documentation files that form the RAG knowledge base. These are realistic, detailed documents modelled on real B2B SaaS support content:

| File | Content |
|------|---------|
| `01_product_overview.md` | Product tiers, pricing, CRM integrations, onboarding timeline |
| `02_crm_integration_guide.md` | Step-by-step setup and troubleshooting for DealerSocket, VinSolutions, CDK Global |
| `03_call_quality_troubleshooting.md` | Transcription accuracy, dropped calls, slow responses, escalation triggers |
| `04_billing_and_payments.md` | Invoice structure, payment failure flow, refund policy, plan changes |
| `05_tcpa_compliance.md` | TCPA rules, DNC registry, SMS opt-out handling, call recording consent |
| `06_onboarding_guide.md` | Full onboarding flow from account setup to go-live, FAQ |

Each document was written to:
- Cover the exact question categories the Triage Agent classifies
- Include actionable step-by-step instructions so the Resolution Agent can cite specific steps
- Contain enough detail that RAG retrieval returns genuinely useful chunks (not just keyword matches)

### 2. RAG Pipeline (`src/rag.py`)

- Built the full retrieval-augmented generation pipeline using ChromaDB and LangChain
- Implemented document loading using `TextLoader` for all Markdown files in `knowledge_base/`
- Configured `RecursiveCharacterTextSplitter` with `chunk_size=800, chunk_overlap=100` — tuned to keep step-by-step instructions intact within a single chunk
- Used `text-embedding-3-small` OpenAI embeddings for cost-efficient, high-quality semantic search
- Implemented lazy vectorstore initialisation: builds from documents on first run, loads from disk on subsequent runs (avoids re-embedding on every app restart)
- Exposed `search_kb(query, k=4)` returning ranked results with source file and relevance score
- Implemented `rebuild_vectorstore()` utility for when KB documents are updated

### 3. Triage Agent (`src/agents.py` — `triage_agent`)

- Implemented the Triage Agent using `ChatOpenAI` with `with_structured_output(TicketCategory)`
- Designed the classification prompt covering all six ticket categories with explicit disambiguation rules (e.g. when a billing issue also has an angry tone — which field takes precedence)
- Defined urgency escalation criteria: `critical` for legal/data threats, `high` for angry cancellation threats, `medium` for broken functionality, `low` for how-to questions
- Defined sentiment scale: `positive`, `neutral`, `frustrated`, `angry` with concrete linguistic markers for each
- Outputs confidence score (0–1) alongside reasoning string for observability

### 4. Knowledge Agent (`src/agents.py` — `knowledge_agent`)

- Implemented the Knowledge Agent that performs RAG search based on triage context
- Built a category-to-query mapping that appends domain-specific search terms based on the Triage Agent's classification — improves retrieval relevance significantly over raw ticket text alone
- Converts raw search results into typed `KBSearchResult` objects with source attribution
- Logs the top source file and chunk count to the agent trace for debugging

### 5. Resolution Agent (`src/agents.py` — `resolution_agent`)

- Implemented the Resolution Agent that drafts the customer response
- Designed prompt to use KB context directly, with strict instruction not to fabricate policies or features not found in the knowledge base
- Implemented tone mapping: maps `angry` sentiment to `apologetic` tone, `frustrated` to `empathetic`, neutral/positive to `professional`
- If the Quality Agent rejects a draft, the previous issues are injected into the Resolution Agent's next prompt so it can directly address the flagged problems
- Output is a structured `ResolutionDraft` with subject, body, tone, and suggested follow-up actions

---

## Files Owned

| File | Description |
|------|-------------|
| `src/rag.py` | ChromaDB vector store, document loading, chunking, search |
| `knowledge_base/01_product_overview.md` | Product overview document |
| `knowledge_base/02_crm_integration_guide.md` | CRM integration guide |
| `knowledge_base/03_call_quality_troubleshooting.md` | Call quality troubleshooting |
| `knowledge_base/04_billing_and_payments.md` | Billing and payments guide |
| `knowledge_base/05_tcpa_compliance.md` | TCPA compliance guide |
| `knowledge_base/06_onboarding_guide.md` | Onboarding guide |
| `src/agents.py` (Triage, Knowledge, Resolution) | Three core agent implementations |

---

## Design Decisions I Made

- **Why chunk size 800 with overlap 100:** Smaller chunks (e.g. 400) split step-by-step instructions across chunks, causing the retrieval to miss half the steps. Larger chunks (e.g. 1200) reduce retrieval precision. 800 was the sweet spot for this KB structure.
- **Why category-augmented queries in the Knowledge Agent:** The raw ticket text is often too colloquial for semantic search (e.g. "it's not working"). Appending category-specific technical terms to the query dramatically improves retrieval relevance.
- **Why structured output for Triage:** The downstream routing logic reads `.category` and `.urgency` as exact strings. A free-text response would require fragile parsing. Structured output eliminates that risk.
- **Why inject previous quality issues into the Resolution Agent's retry prompt:** Simply re-running the same prompt produces the same output. The retry only works if the agent knows what was wrong with the previous attempt.
