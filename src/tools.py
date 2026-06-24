import json
import random
from datetime import datetime
from typing import Any

from langchain_core.tools import tool

from src.rag import search_kb


@tool
def search_knowledge_base(query: str) -> str:
    """Search the AutoVoice AI knowledge base for relevant information to resolve a support ticket."""
    results = search_kb(query, k=4)
    if not results:
        return "No relevant information found in the knowledge base."
    output = []
    for r in results:
        output.append(
            f"[Source: {r['source']} | Relevance: {r['relevance_score']}]\n{r['content']}"
        )
    return "\n\n---\n\n".join(output)


@tool
def lookup_account(account_id: str) -> str:
    """Look up a dealership account by ID to retrieve plan, usage, and status information."""
    mock_accounts = {
        "ACC001": {
            "dealership": "Sunrise Ford",
            "plan": "Growth",
            "monthly_minutes_used": 2800,
            "monthly_minutes_limit": 3000,
            "sms_used": 4200,
            "sms_limit": 6000,
            "payment_status": "current",
            "crm": "DealerSocket",
            "account_age_months": 14,
            "open_tickets": 1,
        },
        "ACC002": {
            "dealership": "Metro Toyota",
            "plan": "Starter",
            "monthly_minutes_used": 1100,
            "monthly_minutes_limit": 1000,
            "sms_used": 1800,
            "sms_limit": 2000,
            "payment_status": "overdue_7_days",
            "crm": "VinSolutions",
            "account_age_months": 3,
            "open_tickets": 0,
        },
        "ACC003": {
            "dealership": "Prestige BMW",
            "plan": "Enterprise",
            "monthly_minutes_used": 8400,
            "monthly_minutes_limit": 99999,
            "sms_used": 12000,
            "sms_limit": 99999,
            "payment_status": "current",
            "crm": "CDK Global",
            "account_age_months": 28,
            "open_tickets": 2,
        },
    }
    account = mock_accounts.get(account_id.upper())
    if not account:
        return f"No account found with ID '{account_id}'. Verify the account ID or search by dealership name."
    return json.dumps(account, indent=2)


@tool
def send_response_email(to_email: str, subject: str, body: str, ticket_id: str) -> str:
    """Send the final resolution email to the customer. This is a high-impact action requiring prior human approval."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    confirmation_id = f"SENT-{random.randint(100000, 999999)}"
    return json.dumps(
        {
            "status": "sent",
            "confirmation_id": confirmation_id,
            "to": to_email,
            "subject": subject,
            "ticket_id": ticket_id,
            "sent_at": timestamp,
            "message": f"Email successfully delivered. Confirmation: {confirmation_id}",
        }
    )


@tool
def flag_compliance_issue(ticket_id: str, issue_type: str, description: str) -> str:
    """Flag a ticket as a compliance or legal issue. Notifies the compliance team and locks the ticket from auto-resolution."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    flag_id = f"COMP-{random.randint(10000, 99999)}"
    return json.dumps(
        {
            "flag_id": flag_id,
            "ticket_id": ticket_id,
            "issue_type": issue_type,
            "description": description,
            "compliance_team_notified": True,
            "flagged_at": timestamp,
            "next_steps": "Compliance team will review within 2 business hours. Legal hold applied to call recordings.",
        }
    )


@tool
def create_escalation_ticket(
    original_ticket_id: str,
    escalation_team: str,
    priority: str,
    summary: str,
    customer_email: str,
) -> str:
    """Create an internal escalation ticket and assign it to the appropriate team."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    esc_id = f"ESC-{random.randint(10000, 99999)}"
    return json.dumps(
        {
            "escalation_id": esc_id,
            "assigned_to": escalation_team,
            "priority": priority,
            "original_ticket": original_ticket_id,
            "summary": summary,
            "customer_email": customer_email,
            "created_at": timestamp,
            "sla_hours": {"normal": 24, "urgent": 4, "immediate": 1}.get(priority, 24),
            "status": "open",
        }
    )
