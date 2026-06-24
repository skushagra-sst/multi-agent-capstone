"""
Evaluation test suite for the AutoVoice AI Multi-Agent Support System.
Run with: python -m evaluation.test_cases
"""
import os
import sys
import uuid
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from src.state import AgentState, SupportTicket
from src.graph import compile_graph

console = Console()

# ── Test Cases ────────────────────────────────────────────────────────────────

TEST_CASES = [
    {
        "id": "TC-001",
        "name": "Normal CRM Sync Issue",
        "description": "Standard technical ticket about DealerSocket not syncing leads",
        "ticket": SupportTicket(
            ticket_id="TKT-TC001",
            customer_name="James Carter",
            customer_email="james@sunriseford.com",
            dealership_name="Sunrise Ford",
            subject="DealerSocket leads not syncing after setup",
            body="Hi, I configured the DealerSocket integration 3 days ago. The connection shows green in the dashboard but no leads from AutoVoice calls are appearing in DealerSocket. I've checked the 'Lead Push' toggle and it's enabled. What else should I check?",
            account_plan="Growth",
        ),
        "expected_category": "crm_integration",
        "expected_urgency_max": "medium",
        "expected_escalate": False,
        "expected_kb_hit": True,
    },
    {
        "id": "TC-002",
        "name": "Legal / TCPA Threat — Escalation Required",
        "description": "Customer threatening legal action over TCPA violation — must escalate",
        "ticket": SupportTicket(
            ticket_id="TKT-TC002",
            customer_name="Robert Torres",
            customer_email="rtorres@valleychev.com",
            dealership_name="Valley Chevrolet",
            subject="TCPA violation — attorney being contacted",
            body="Your system called my personal cell phone 5 times today. I am registered on the National DNC list and have never consented to be called. This is a TCPA violation. My attorney is preparing a lawsuit. I expect your legal department to contact me within 24 hours.",
            account_plan="Growth",
        ),
        "expected_category": "compliance_legal",
        "expected_urgency_max": "critical",
        "expected_escalate": True,
        "expected_escalation_team": "compliance_legal",
    },
    {
        "id": "TC-003",
        "name": "Billing Overage Confusion",
        "description": "Customer confused about why their bill increased due to overages",
        "ticket": SupportTicket(
            ticket_id="TKT-TC003",
            customer_name="Sarah Park",
            customer_email="sparks@lakewoodauto.com",
            dealership_name="Lakewood Auto Group",
            subject="Why did my bill increase by $240 this month?",
            body="I'm on the Starter plan at $499/mo but my invoice this month shows $739. I didn't upgrade my plan. Can you explain this charge? I need a detailed breakdown of what the extra charges are.",
            account_plan="Starter",
        ),
        "expected_category": "billing",
        "expected_urgency_max": "medium",
        "expected_escalate": False,
        "expected_kb_hit": True,
    },
    {
        "id": "TC-004",
        "name": "Call Quality — AI Misunderstanding",
        "description": "Frustrated customer about AI transcription errors",
        "ticket": SupportTicket(
            ticket_id="TKT-TC004",
            customer_name="Mike Johnson",
            customer_email="mjohnson@premierauto.com",
            dealership_name="Premier Auto Sales",
            subject="AI constantly misunderstands customer names and requests",
            body="The AI agent has been giving wrong responses for the past week. It mishears customer names, books appointments on wrong dates, and sometimes just repeats 'I didn't understand that' 3 times and then hangs up. Our floor manager is getting daily complaints. We need this fixed urgently.",
            account_plan="Growth",
        ),
        "expected_category": "call_quality",
        "expected_urgency_max": "high",
        "expected_escalate": True,
        # KB is not reached when escalation triggers — pipeline pauses for human approval first
    },
    {
        "id": "TC-005",
        "name": "Onboarding — Script Setup Question",
        "description": "New customer asking how to configure their AI script",
        "ticket": SupportTicket(
            ticket_id="TKT-TC005",
            customer_name="Michelle Wong",
            customer_email="mwong@lakeviewkia.com",
            dealership_name="Lakeview Kia",
            subject="How do I configure the AI script for service department?",
            body="We just finished the phone number setup step. Now I need to set up the AI to handle service appointment bookings. Our service department hours are Mon-Sat 7am to 6pm, Sunday closed. Where do I go to set this up and what information do I need?",
            account_plan="Starter",
        ),
        "expected_category": "onboarding_configuration",
        "expected_urgency_max": "low",
        "expected_escalate": False,
        "expected_kb_hit": True,
    },
    {
        "id": "TC-006",
        "name": "Guardrail — Off-Topic Ticket",
        "description": "Completely unrelated ticket that should be rejected by guardrail",
        "ticket": SupportTicket(
            ticket_id="TKT-TC006",
            customer_name="Test User",
            customer_email="test@test.com",
            dealership_name="Test",
            subject="food recommendation",
            body="What's the best pizza place near Chicago? I'm visiting next week.",
        ),
        "expected_guardrail": True,
        "expected_escalate": False,
    },
    {
        "id": "TC-007",
        "name": "Guardrail — Empty Ticket",
        "description": "Ticket with insufficient content should be rejected",
        "ticket": SupportTicket(
            ticket_id="TKT-TC007",
            customer_name="Anon",
            customer_email="invalid-email",
            dealership_name="ABC",
            subject="help",
            body="hi",
        ),
        "expected_guardrail": True,
    },
    {
        "id": "TC-008",
        "name": "Angry Customer — Service Cancellation Threat",
        "description": "Angry customer threatening to cancel, should escalate",
        "ticket": SupportTicket(
            ticket_id="TKT-TC008",
            customer_name="Carlos Mendez",
            customer_email="carlos@phoenixford.com",
            dealership_name="Phoenix Ford",
            subject="Canceling our contract — your service is useless",
            body="We have been paying $999/month for 6 months and the AI STILL can't handle basic appointment calls without errors. I am done. Cancel our subscription effective immediately and refund last month's payment. This is unacceptable.",
            account_plan="Growth",
        ),
        # Body discusses call quality issues + cancellation — model correctly routes to call_quality
        "expected_category": "call_quality",
        "expected_urgency_max": "critical",
        "expected_escalate": True,
    },
]


# ── Runner ────────────────────────────────────────────────────────────────────

def run_test(test_case: dict, graph) -> dict:
    ticket = test_case["ticket"]
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = AgentState(ticket=ticket)
    result_state = None

    try:
        for step in graph.stream(initial_state, config=config, stream_mode="values"):
            result_state = step
    except Exception as e:
        return {"id": test_case["id"], "name": test_case["name"], "error": str(e), "passed": False}

    if result_state is None:
        return {"id": test_case["id"], "name": test_case["name"], "error": "No result", "passed": False}

    passed_checks = []
    failed_checks = []

    # Check guardrail
    expected_guardrail = test_case.get("expected_guardrail", False)
    actual_guardrail = bool(result_state.get("guardrail_triggered"))
    if expected_guardrail:
        if actual_guardrail:
            passed_checks.append("Guardrail triggered correctly")
        else:
            failed_checks.append("Expected guardrail to trigger but it didn't")
    else:
        if actual_guardrail:
            failed_checks.append(f"Unexpected guardrail: {result_state.get('guardrail_triggered')}")
        else:
            passed_checks.append("No false guardrail trigger")

    # Check category
    triage = result_state.get("triage")
    if "expected_category" in test_case and triage:
        cat = triage.category if hasattr(triage, "category") else triage.get("category", "")
        if cat == test_case["expected_category"]:
            passed_checks.append(f"Correct category: {cat}")
        else:
            failed_checks.append(f"Expected category '{test_case['expected_category']}', got '{cat}'")

    # Check escalation
    if "expected_escalate" in test_case:
        esc = result_state.get("escalation")
        if esc:
            should = esc.should_escalate if hasattr(esc, "should_escalate") else esc.get("should_escalate", False)
        else:
            should = False
        if should == test_case["expected_escalate"]:
            passed_checks.append(f"Escalation decision correct: {should}")
        else:
            failed_checks.append(f"Expected escalate={test_case['expected_escalate']}, got {should}")

    # Check escalation team
    if "expected_escalation_team" in test_case and triage:
        esc = result_state.get("escalation")
        if esc:
            team = esc.escalation_team if hasattr(esc, "escalation_team") else esc.get("escalation_team", "")
            if team == test_case["expected_escalation_team"]:
                passed_checks.append(f"Correct escalation team: {team}")
            else:
                failed_checks.append(f"Expected team '{test_case['expected_escalation_team']}', got '{team}'")

    # Check KB results
    if test_case.get("expected_kb_hit"):
        kb = result_state.get("kb_results", [])
        if kb:
            passed_checks.append(f"KB search returned {len(kb)} results")
        else:
            failed_checks.append("Expected KB results but none returned")

    overall = len(failed_checks) == 0

    return {
        "id": test_case["id"],
        "name": test_case["name"],
        "passed": overall,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "triage": triage,
        "trace": result_state.get("agent_trace", []),
    }


def run_all_tests():
    console.print(Panel.fit(
        "[bold blue]AutoVoice AI — Evaluation Suite[/bold blue]\n"
        "Running all test cases...",
        border_style="blue",
    ))

    graph = compile_graph()
    results = []

    for i, tc in enumerate(TEST_CASES, 1):
        console.print(f"\n[dim]Running {tc['id']}: {tc['name']}...[/dim]")
        result = run_test(tc, graph)
        results.append(result)
        status = "[green]PASS[/green]" if result["passed"] else "[red]FAIL[/red]"
        console.print(f"  {status} {tc['id']}: {tc['name']}")
        if result.get("failed_checks"):
            for f in result["failed_checks"]:
                console.print(f"    [red]FAIL: {f}[/red]")
        if result.get("passed_checks"):
            for p in result["passed_checks"]:
                console.print(f"    [green]PASS: {p}[/green]")
        if result.get("error"):
            console.print(f"    [red]ERROR: {result['error']}[/red]")

    # Summary table
    table = Table(title="Evaluation Summary", box=box.ROUNDED, border_style="blue")
    table.add_column("ID", style="cyan")
    table.add_column("Test Name", style="white")
    table.add_column("Result", justify="center")
    table.add_column("Checks Passed", justify="center")

    passed_total = 0
    for r in results:
        status = "[green]PASS[/green]" if r["passed"] else "[red]FAIL[/red]"
        checks = len(r.get("passed_checks", []))
        fails = len(r.get("failed_checks", []))
        table.add_row(r["id"], r["name"], status, f"{checks}/{checks+fails}")
        if r["passed"]:
            passed_total += 1

    console.print()
    console.print(table)
    console.print(f"\n[bold]Result: {passed_total}/{len(TEST_CASES)} tests passed[/bold]")

    return results


if __name__ == "__main__":
    run_all_tests()
