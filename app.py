import uuid
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.state import AgentState, SupportTicket
from src.graph import compile_graph

st.set_page_config(
    page_title="AutoVoice AI — Support",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }

.stApp { background: #f5f5f4; }
.block-container { padding: 1.75rem 2rem 2rem 2rem !important; max-width: 1200px !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #1c1917 !important;
    min-width: 210px !important; max-width: 210px !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: #a8a29e !important; }
[data-testid="stSidebar"] button {
    background: #292524 !important; border: 1px solid #3c3835 !important;
    color: #d6d3d1 !important; border-radius: 5px !important;
    font-size: 0.78rem !important; font-weight: 500 !important;
    padding: 0.35rem 0.7rem !important; margin-bottom: 3px !important;
    text-align: left !important;
}
[data-testid="stSidebar"] button:hover { background: #3c3835 !important; }
[data-testid="stSidebar"] hr { border-color: #292524 !important; }

/* ── Cards ── */
.card {
    background: #fff; border: 1px solid #e7e5e4;
    border-radius: 8px; padding: 1.4rem 1.5rem;
    margin-bottom: 0; 
}

/* ── Column headers ── */
.col-header {
    font-size: 0.68rem; font-weight: 700; color: #78716c;
    text-transform: uppercase; letter-spacing: 0.07em;
    margin-bottom: 0.75rem;
}

/* ── Ticket summary (left, post-submit) ── */
.ticket-id-badge {
    display: inline-block; font-size: 0.7rem; font-weight: 600;
    background: #f5f5f4; border: 1px solid #e7e5e4;
    color: #57534e; padding: 2px 9px; border-radius: 4px;
    margin-bottom: 0.75rem;
}
.ticket-subject { font-size: 1rem; font-weight: 700; color: #1c1917; margin-bottom: 0.35rem; }
.ticket-meta    { font-size: 0.8rem; color: #78716c; line-height: 2; }
.ticket-meta b  { color: #44403c; }
.message-box {
    background: #fafaf9; border: 1px solid #e7e5e4;
    border-radius: 6px; padding: 0.75rem 1rem;
    font-size: 0.82rem; color: #44403c; line-height: 1.7;
    margin-top: 0.75rem; max-height: 180px; overflow-y: auto;
}

/* ── Tags / badges ── */
.tag {
    display: inline-block; font-size: 0.68rem; font-weight: 600;
    padding: 2px 8px; border-radius: 3px; margin-right: 4px;
}
.t-blue   { background: #dbeafe; color: #1d4ed8; }
.t-green  { background: #dcfce7; color: #15803d; }
.t-yellow { background: #fef9c3; color: #a16207; }
.t-orange { background: #ffedd5; color: #c2410c; }
.t-red    { background: #fee2e2; color: #b91c1c; }
.t-purple { background: #f3e8ff; color: #7e22ce; }
.t-stone  { background: #f5f5f4; color: #57534e; }

/* ── Pipeline step rows ── */
.step-row {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 0.85rem 0; border-bottom: 1px solid #f5f5f4;
}
.step-row:last-child { border-bottom: none; }
.step-num {
    width: 22px; height: 22px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.65rem; font-weight: 700; flex-shrink: 0; margin-top: 1px;
}
.sn-done    { background: #16a34a; color: #fff; }
.sn-active  { background: #1c1917; color: #fff; }
.sn-pending { background: #e7e5e4; color: #a8a29e; }
.sn-error   { background: #dc2626; color: #fff; }
.step-body  { flex: 1; min-width: 0; }
.step-label { font-size: 0.7rem; font-weight: 700; color: #78716c; text-transform: uppercase; letter-spacing: 0.05em; }
.step-value { font-size: 0.85rem; color: #1c1917; margin-top: 3px; line-height: 1.5; }
.step-tags  { margin-top: 6px; }
.step-status-dot {
    width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; margin-top: 8px;
}
.sd-done    { background: #16a34a; }
.sd-pending { background: #d6d3d1; }
.sd-active  { background: #1c1917; }
.sd-error   { background: #dc2626; }

/* ── Human review panel ── */
.review-panel {
    border: 1.5px solid #e7e5e4; border-radius: 8px;
    overflow: hidden; margin-top: 0.75rem;
}
.review-panel-header {
    background: #fafaf9; border-bottom: 1px solid #e7e5e4;
    padding: 0.75rem 1rem; font-size: 0.8rem; font-weight: 600; color: #44403c;
}
.review-panel-body { padding: 1rem; }

/* ── Email preview ── */
.email-wrap { border: 1px solid #e7e5e4; border-radius: 6px; overflow: hidden; margin-top: 0.5rem; }
.email-header-row { background: #fafaf9; border-bottom: 1px solid #e7e5e4; padding: 0.65rem 0.9rem; }
.email-subj { font-size: 0.85rem; font-weight: 700; color: #1c1917; }
.email-to   { font-size: 0.73rem; color: #78716c; margin-top: 1px; }
.email-body { padding: 0.9rem; font-size: 0.83rem; color: #292524; line-height: 1.75; white-space: pre-wrap; max-height: 260px; overflow-y: auto; }

/* ── Result banners ── */
.result-banner {
    border-radius: 6px; padding: 1rem 1.2rem; margin-bottom: 0.75rem;
    font-size: 0.88rem;
}
.rb-success { background: #f0fdf4; border: 1px solid #bbf7d0; color: #14532d; }
.rb-warn    { background: #fffbeb; border: 1px solid #fde68a; color: #78350f; }
.rb-error   { background: #fef2f2; border: 1px solid #fecaca; color: #7f1d1d; }

/* ── Agent trace ── */
.trace-line { font-family: 'Menlo', 'Monaco', monospace; font-size: 0.69rem; color: #78716c; padding: 1px 0; line-height: 1.6; }

/* ── Divider ── */
.section-divider { 
    border: none; border-top: 1px solid #e7e5e4; margin: 1rem 0;
}

/* ── Pending step indicator ── */
.pending-row {
    display: flex; align-items: center; gap: 10px;
    padding: 0.6rem 0; color: #a8a29e; font-size: 0.8rem;
    border-bottom: 1px solid #f5f5f4;
}
.pending-row:last-child { border-bottom: none; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def ga(obj, key, default=""):
    if obj is None: return default
    v = getattr(obj, key, None)
    if v is None and isinstance(obj, dict): v = obj.get(key)
    return v if v is not None else default

def tag(text, cls="t-stone"):
    return f'<span class="tag {cls}">{text}</span>'

URGENCY_CLS = {"low":"t-green","medium":"t-yellow","high":"t-orange","critical":"t-red"}
SENT_CLS    = {"positive":"t-green","neutral":"t-stone","frustrated":"t-orange","angry":"t-red"}
CAT_CLS     = {"call_quality":"t-blue","crm_integration":"t-purple","billing":"t-yellow",
               "onboarding_configuration":"t-green","compliance_legal":"t-red","other":"t-stone"}
SLA_MAP     = {"immediate":"1 hour","urgent":"4 hours","normal":"24 hours"}

# ── Session state ─────────────────────────────────────────────────────────────
PIPELINE_KEYS = {"graph","thread_id","agent_state","awaiting_esc","awaiting_resp","done","submitted"}
DEFAULTS = {"graph":None,"thread_id":None,"agent_state":None,
            "awaiting_esc":False,"awaiting_resp":False,"done":False,"submitted":False}
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k]=v

def get_graph():
    if not st.session_state.graph:
        st.session_state.graph = compile_graph()
    return st.session_state.graph

def run_graph(state, thread_id):
    g = get_graph(); cfg = {"configurable":{"thread_id":thread_id}}
    r = None
    for s in g.stream(state, config=cfg, stream_mode="values"): r = s
    return r

def resume_graph(thread_id, updated):
    g = get_graph(); cfg = {"configurable":{"thread_id":thread_id}}
    g.update_state(cfg, updated)
    r = None
    for s in g.stream(None, config=cfg, stream_mode="values"): r = s
    return r

def reset_session():
    for k in PIPELINE_KEYS:
        if k in st.session_state: del st.session_state[k]


# ── Demo data ─────────────────────────────────────────────────────────────────
DEMOS = {
    "CRM Sync Issue": {
        "customer_name":"James Carter","customer_email":"james@sunriseford.com",
        "dealership_name":"Sunrise Ford","account_plan":"Growth",
        "subject":"DealerSocket leads not syncing after setup",
        "body":"Hi, I configured the DealerSocket integration 3 days ago. The connection shows green in the dashboard but no leads from AutoVoice calls are appearing in DealerSocket. I checked the Lead Push toggle and it's enabled. What else should I check?",
    },
    "AI Quality — Urgent": {
        "customer_name":"Sarah Mills","customer_email":"sarah@metrotoyota.com",
        "dealership_name":"Metro Toyota","account_plan":"Starter",
        "subject":"AI keeps misunderstanding customers, losing deals",
        "body":"Your AI is terrible. It keeps mishearing customer names and giving wrong appointment times. We have already lost 3 deals this week because of this. The transcription accuracy is awful and customers are complaining. We need this fixed today or we are canceling.",
    },
    "Billing Confusion": {
        "customer_name":"David Kim","customer_email":"david@prestigebmw.com",
        "dealership_name":"Prestige BMW","account_plan":"Enterprise",
        "subject":"Double charged this month",
        "body":"I noticed we were charged twice for our monthly subscription this month. Both charges appeared on June 1st. Please explain this and issue a refund for the duplicate charge as soon as possible.",
    },
    "TCPA Legal Threat": {
        "customer_name":"Robert Torres","customer_email":"rtorres@valleychev.com",
        "dealership_name":"Valley Chevrolet","account_plan":"Growth",
        "subject":"TCPA violation — attorney being contacted",
        "body":"Your system called my personal cell phone 4 times today despite me being on the DNC list. This is a clear TCPA violation. I have spoken with my attorney and we are preparing a complaint to the FTC. I expect an immediate response from your legal team.",
    },
    "Guardrail Test": {
        "customer_name":"Test User","customer_email":"test@example.com",
        "dealership_name":"Test Dealership","account_plan":"Starter",
        "subject":"Quick question",
        "body":"Hey what is the best pizza place near downtown Chicago?",
    },
    "Onboarding Help": {
        "customer_name":"Michelle Wong","customer_email":"mwong@lakeviewkia.com",
        "dealership_name":"Lakeview Kia","account_plan":"Starter",
        "subject":"How to set up AI script for service department",
        "body":"We just finished the phone number setup step. Now I need to configure the AI to handle service appointment bookings. Our service hours are Monday through Saturday 7am to 6pm, Sunday closed. Where do I go and what information do I need?",
    },
}


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<p style='color:#e7e5e4;font-weight:700;font-size:0.95rem;margin:0 0 2px'>AutoVoice AI</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.72rem;color:#57534e;margin:0'>Support Demo</p>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<p style='font-size:0.65rem;font-weight:700;color:#57534e;text-transform:uppercase;letter-spacing:.07em;margin-bottom:5px'>Demo Scenarios</p>", unsafe_allow_html=True)
    for label in DEMOS:
        if st.button(label, use_container_width=True, key=f"btn_{label}"):
            reset_session()
            for k, v in DEMOS[label].items():
                st.session_state[f"form_{k}"] = v
            st.rerun()
    st.divider()
    if st.button("New Ticket", use_container_width=True, key="btn_reset"):
        reset_session()
        for k in list(st.session_state.keys()):
            if k.startswith("form_"): del st.session_state[k]
        st.rerun()
    st.markdown("""
<div style='margin-top:1.2rem'>
<p style='font-size:0.65rem;font-weight:700;color:#57534e;text-transform:uppercase;letter-spacing:.07em;margin-bottom:8px'>Agents</p>
<div style='font-size:0.75rem;color:#78716c;line-height:2.2'>
1. Guardrail<br>2. Triage<br>3. Escalation Check<br>4. Knowledge (RAG)<br>5. Resolution Draft<br>6. Quality Review<br>7. Human-in-the-Loop
</div></div>""", unsafe_allow_html=True)


# ── State ─────────────────────────────────────────────────────────────────────
state = st.session_state.agent_state

def get_stage():
    if not st.session_state.submitted: return "idle"
    if ga(state, "guardrail_triggered"):  return "rejected"
    if st.session_state.done:            return "done"
    if st.session_state.awaiting_esc:    return "esc_review"
    if st.session_state.awaiting_resp:   return "resp_review"
    return "idle"

S = get_stage()


# ── Layout: two fixed columns ─────────────────────────────────────────────────
left, right = st.columns([4, 6], gap="large")


# ════════════════════════════════════════
# LEFT COLUMN
# ════════════════════════════════════════
with left:
    st.markdown('<div class="col-header">Ticket</div>', unsafe_allow_html=True)

    if S == "idle":
        # Form
        with st.container(border=False):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            with st.form("ticket_form", border=False):
                c1, c2 = st.columns(2)
                cname  = c1.text_input("Customer Name",  value=st.session_state.get("form_customer_name",""))
                cemail = c2.text_input("Email",           value=st.session_state.get("form_customer_email",""))
                c3, c4 = st.columns(2)
                dealer = c3.text_input("Dealership",     value=st.session_state.get("form_dealership_name",""))
                opts   = ["","Starter","Growth","Enterprise"]
                saved  = st.session_state.get("form_account_plan","")
                plan   = c4.selectbox("Plan", opts, index=opts.index(saved) if saved in opts else 0)
                subj   = st.text_input("Subject",         value=st.session_state.get("form_subject",""))
                body   = st.text_area("Message", height=150, value=st.session_state.get("form_body",""))
                go     = st.form_submit_button("Submit Ticket", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if go:
            if not all([cname, cemail, dealer, subj, body]):
                st.error("Please fill in all fields.")
            else:
                ticket = SupportTicket(
                    ticket_id=f"TKT-{uuid.uuid4().hex[:6].upper()}",
                    customer_name=cname, customer_email=cemail,
                    dealership_name=dealer, subject=subj, body=body,
                    account_plan=plan or None,
                )
                tid = str(uuid.uuid4())
                st.session_state.thread_id = tid
                with st.spinner("Processing..."):
                    result = run_graph(AgentState(ticket=ticket), tid)
                st.session_state.agent_state = result
                st.session_state.submitted   = True
                if ga(result, "guardrail_triggered"):
                    st.session_state.done = True
                elif ga(result.get("escalation"), "should_escalate"):
                    st.session_state.awaiting_esc = True
                elif result.get("resolution_draft"):
                    st.session_state.awaiting_resp = True
                else:
                    st.session_state.done = True
                st.rerun()
    else:
        # Ticket summary card
        td = state.get("ticket", {})
        st.markdown(f'<div class="ticket-id-badge">{ga(td,"ticket_id")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ticket-subject">{ga(td,"subject")}</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div class="ticket-meta">
  <b>From</b> &nbsp; {ga(td,"customer_name")}<br>
  <b>Email</b> &nbsp; {ga(td,"customer_email")}<br>
  <b>Dealership</b> &nbsp; {ga(td,"dealership_name")}<br>
  <b>Plan</b> &nbsp; {ga(td,"account_plan","—")}
</div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="message-box">{ga(td,"body")}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════
# RIGHT COLUMN
# ════════════════════════════════════════
with right:
    st.markdown('<div class="col-header">Agent Pipeline</div>', unsafe_allow_html=True)

    if S == "idle":
        st.markdown("""
<div style='padding:3rem 0;text-align:center;color:#a8a29e;font-size:0.85rem'>
Submit a ticket to see the agent pipeline run step by step.
</div>""", unsafe_allow_html=True)

    else:
        st.markdown('<div class="card" style="padding:0.5rem 1.25rem">', unsafe_allow_html=True)

        triage = state.get("triage")
        esc    = state.get("escalation")
        kb     = state.get("kb_results", [])
        draft  = state.get("resolution_draft")
        quality = state.get("quality_check")

        # ── STEP 1: Guardrail ─────────────────────────────────────
        if S == "rejected":
            num_cls, dot_cls = "sn-error", "sd-error"
            value_html = f'<div class="step-value" style="color:#b91c1c">{ga(state,"guardrail_triggered")}</div>'
            status_tag = tag("Rejected","t-red")
        else:
            num_cls, dot_cls = "sn-done", "sd-done"
            value_html = '<div class="step-value">Ticket passed all validation checks.</div>'
            status_tag = tag("Passed","t-green")

        st.markdown(f"""
<div class="step-row">
  <div class="step-num {num_cls}">{'X' if S=='rejected' else '1'}</div>
  <div class="step-body">
    <div class="step-label">Guardrail</div>
    {value_html}
  </div>
  {status_tag}
</div>""", unsafe_allow_html=True)

        # ── STEP 2: Triage ────────────────────────────────────────
        if triage:
            cat    = ga(triage,"category","other")
            urg    = ga(triage,"urgency","low")
            sent   = ga(triage,"sentiment","neutral")
            conf   = ga(triage,"confidence",0)
            reason = ga(triage,"reasoning","")
            tags_html = (
                tag(cat.replace("_"," ").title(), CAT_CLS.get(cat,"t-stone")) +
                tag(urg.capitalize(), URGENCY_CLS.get(urg,"t-stone")) +
                tag(sent.capitalize(), SENT_CLS.get(sent,"t-stone")) +
                tag(f"{int(conf*100)}% conf","t-stone")
            )
            st.markdown(f"""
<div class="step-row">
  <div class="step-num sn-done">2</div>
  <div class="step-body">
    <div class="step-label">Triage Agent</div>
    <div class="step-value">{reason}</div>
    <div class="step-tags">{tags_html}</div>
  </div>
</div>""", unsafe_allow_html=True)
        elif S != "rejected":
            st.markdown('<div class="pending-row"><div class="step-num sn-pending">2</div><span style="font-size:0.75rem;color:#a8a29e">Triage Agent — pending</span></div>', unsafe_allow_html=True)

        # ── STEP 3: Escalation Check ──────────────────────────────
        if esc:
            should   = ga(esc,"should_escalate",False)
            reason_e = ga(esc,"reason","")
            team     = ga(esc,"escalation_team","—")
            priority = ga(esc,"priority","normal")
            if should and S == "esc_review":
                num_cls = "sn-active"
                esc_val = f'Escalation recommended — {team.replace("_"," ").title()}, {priority} priority'
                esc_tag = tag("Awaiting approval","t-orange")
            elif should:
                num_cls = "sn-done"
                esc_val = f'Escalated to {team.replace("_"," ").title()}'
                esc_tag = tag("Escalated","t-orange")
            else:
                num_cls = "sn-done"
                esc_val = reason_e
                esc_tag = tag("No escalation","t-green")
            st.markdown(f"""
<div class="step-row">
  <div class="step-num {num_cls}">3</div>
  <div class="step-body">
    <div class="step-label">Escalation Check</div>
    <div class="step-value">{esc_val}</div>
  </div>
  {esc_tag}
</div>""", unsafe_allow_html=True)
        elif S not in ("rejected",):
            st.markdown('<div class="pending-row"><div class="step-num sn-pending">3</div><span style="font-size:0.75rem;color:#a8a29e">Escalation Check — pending</span></div>', unsafe_allow_html=True)

        # ── STEP 4: Knowledge Retrieval ───────────────────────────
        if kb:
            sources   = list({ga(r,"source","") for r in kb})
            src_tags  = "".join(tag(s.replace(".md",""),"t-purple") for s in sources)
            st.markdown(f"""
<div class="step-row">
  <div class="step-num sn-done">4</div>
  <div class="step-body">
    <div class="step-label">Knowledge Agent (RAG)</div>
    <div class="step-value">{len(kb)} chunks retrieved</div>
    <div class="step-tags">{src_tags}</div>
  </div>
  {tag("Retrieved","t-green")}
</div>""", unsafe_allow_html=True)
        elif S not in ("rejected","esc_review"):
            st.markdown('<div class="pending-row"><div class="step-num sn-pending">4</div><span style="font-size:0.75rem;color:#a8a29e">Knowledge Agent — pending</span></div>', unsafe_allow_html=True)

        # ── STEP 5: Resolution + Quality ─────────────────────────
        if draft and quality:
            q_passed = ga(quality,"passed",True)
            q_issues = ga(quality,"issues",[])
            if isinstance(q_issues,str): q_issues=[]
            tone     = ga(draft,"tone","")
            q_tag    = tag("QA Passed","t-green") if q_passed else tag(f"{len(q_issues)} issue(s)","t-orange")
            st.markdown(f"""
<div class="step-row">
  <div class="step-num sn-done">5</div>
  <div class="step-body">
    <div class="step-label">Resolution + Quality</div>
    <div class="step-value">Draft written — tone: {tone}{'.' if not q_issues else '. Issues flagged and revised.'}</div>
  </div>
  {q_tag}
</div>""", unsafe_allow_html=True)
        elif S not in ("rejected","esc_review"):
            st.markdown('<div class="pending-row"><div class="step-num sn-pending">5</div><span style="font-size:0.75rem;color:#a8a29e">Resolution + Quality — pending</span></div>', unsafe_allow_html=True)

        # ── STEP 6: Human Review ──────────────────────────────────
        status = ga(state,"send_status","")
        if S in ("resp_review","esc_review"):
            num_cls = "sn-active"
            hitl_val = "Waiting for human approval."
            hitl_tag = tag("Action required","t-orange")
        elif status == "sent":
            num_cls = "sn-done"
            hitl_val = "Response approved and sent."
            hitl_tag = tag("Sent","t-green")
        elif status == "escalated":
            num_cls = "sn-done"
            hitl_val = "Escalation approved."
            hitl_tag = tag("Escalated","t-orange")
        elif S == "done" and ga(state,"guardrail_triggered"):
            num_cls = "sn-pending"
            hitl_val = ""
            hitl_tag = ""
        else:
            num_cls = "sn-pending"
            hitl_val = ""
            hitl_tag = ""

        if hitl_val:
            st.markdown(f"""
<div class="step-row">
  <div class="step-num {num_cls}">6</div>
  <div class="step-body">
    <div class="step-label">Human-in-the-Loop</div>
    <div class="step-value">{hitl_val}</div>
  </div>
  {hitl_tag}
</div>""", unsafe_allow_html=True)
        elif S not in ("rejected","esc_review","resp_review","done"):
            st.markdown('<div class="pending-row"><div class="step-num sn-pending">6</div><span style="font-size:0.75rem;color:#a8a29e">Human-in-the-Loop — pending</span></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # close .card

        # ── Active action panel ────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)

        # ── GUARDRAIL REJECTED ────────────────────────────────────
        if S == "rejected":
            st.markdown(f"""
<div class="result-banner rb-error">
  <b>Ticket rejected.</b> {ga(state,"guardrail_triggered")}
  <br><span style="font-size:0.78rem;opacity:.8;margin-top:4px;display:block">Please resubmit with a valid support-related request.</span>
</div>""", unsafe_allow_html=True)

        # ── ESCALATION REVIEW ─────────────────────────────────────
        elif S == "esc_review":
            team     = ga(esc,"escalation_team","tier2_support")
            priority = ga(esc,"priority","normal")
            reason_e = ga(esc,"reason","")
            sla      = SLA_MAP.get(priority,"24 hours")

            st.markdown(f"""
<div class="review-panel">
  <div class="review-panel-header">Human Review — Escalation Decision</div>
  <div class="review-panel-body">
    <div style="font-size:0.85rem;color:#44403c;margin-bottom:0.8rem">{reason_e}</div>
    <div style="margin-bottom:0.9rem">
      {tag("Team: "+team.replace("_"," ").title(),"t-orange")}
      {tag(priority.capitalize()+" priority", URGENCY_CLS.get(priority,"t-stone"))}
      {tag("SLA: "+sla,"t-stone")}
    </div>
    <div style="font-size:0.8rem;color:#78716c;line-height:1.9;margin-bottom:1rem">
      <b style="color:#44403c">If approved:</b> ticket assigned to the specialist team, customer gets an acknowledgement, team responds within {sla}.<br>
      <b style="color:#44403c">If rejected:</b> agents will attempt to auto-resolve the ticket instead.
    </div>
  </div>
</div>""", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Approve Escalation", type="primary", use_container_width=True):
                    cur = AgentState(**state) if isinstance(state, dict) else state
                    with st.spinner("Escalating..."):
                        result = resume_graph(st.session_state.thread_id, cur.model_copy(update={"human_approved":True}))
                    st.session_state.agent_state = result
                    st.session_state.awaiting_esc = False
                    st.session_state.done = True
                    st.rerun()
            with c2:
                if st.button("Reject — Auto-resolve", use_container_width=True):
                    cur = AgentState(**state) if isinstance(state, dict) else state
                    with st.spinner("Running resolution..."):
                        result = resume_graph(st.session_state.thread_id, cur.model_copy(update={"human_approved":False}))
                    st.session_state.agent_state = result
                    st.session_state.awaiting_esc = False
                    if result.get("resolution_draft"): st.session_state.awaiting_resp = True
                    else:                              st.session_state.done = True
                    st.rerun()

        # ── RESPONSE REVIEW ───────────────────────────────────────
        elif S == "resp_review":
            d_subj    = ga(draft,"subject","")
            d_body    = ga(draft,"body","")
            d_tone    = ga(draft,"tone","")
            d_actions = ga(draft,"suggested_actions",[])
            if isinstance(d_actions, str): d_actions = []
            q_passed  = ga(quality,"passed",True)
            q_issues  = ga(quality,"issues",[])
            if isinstance(q_issues, str): q_issues = []
            td        = state.get("ticket",{})

            qa_banner = (
                f'<div style="font-size:0.78rem;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:4px;padding:6px 10px;color:#14532d;margin-bottom:0.6rem">Quality check passed — tone: {d_tone}</div>'
                if q_passed else
                f'<div style="font-size:0.78rem;background:#fffbeb;border:1px solid #fde68a;border-radius:4px;padding:6px 10px;color:#78350f;margin-bottom:0.6rem">Quality check flagged {len(q_issues)} issue(s)</div>'
            )

            st.markdown(f"""
<div class="review-panel">
  <div class="review-panel-header">Human Review — Response Approval</div>
  <div class="review-panel-body">
    {qa_banner}
    <div class="email-wrap">
      <div class="email-header-row">
        <div class="email-subj">{d_subj}</div>
        <div class="email-to">To: {ga(td,"customer_name")} &lt;{ga(td,"customer_email")}&gt;</div>
      </div>
      <div class="email-body">{d_body}</div>
    </div>
""", unsafe_allow_html=True)

            if d_actions:
                actions_html = "".join(f'<div style="font-size:0.78rem;color:#57534e;padding:2px 0">— {a}</div>' for a in d_actions)
                st.markdown(f'<div style="margin-top:0.7rem"><div style="font-size:0.7rem;font-weight:700;color:#78716c;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">Follow-up actions</div>{actions_html}</div>', unsafe_allow_html=True)

            st.markdown('</div></div>', unsafe_allow_html=True)

            feedback = st.text_input("Add a note (optional):", placeholder="e.g. Offer a 15-min call with a CRM specialist", key="fb")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Approve and Send", type="primary", use_container_width=True):
                    cur = AgentState(**state) if isinstance(state, dict) else state
                    with st.spinner("Sending..."):
                        result = resume_graph(st.session_state.thread_id, cur.model_copy(update={"human_approved":True,"human_feedback":feedback or None}))
                    st.session_state.agent_state  = result
                    st.session_state.awaiting_resp = False
                    st.session_state.done          = True
                    st.rerun()
            with c2:
                if st.button("Reject and Revise", use_container_width=True):
                    cur = AgentState(**state) if isinstance(state, dict) else state
                    with st.spinner("Revising..."):
                        result = resume_graph(st.session_state.thread_id, cur.model_copy(update={"human_approved":False,"human_feedback":feedback or None}))
                    st.session_state.agent_state  = result
                    st.session_state.awaiting_resp = False
                    if result.get("resolution_draft"): st.session_state.awaiting_resp = True
                    else:                              st.session_state.done = True
                    st.rerun()

        # ── DONE ─────────────────────────────────────────────────
        elif S == "done":
            if status == "sent":
                fb = ga(state,"human_feedback")
                td = state.get("ticket",{})
                d_subj = ga(draft,"subject","") if draft else ""
                d_body = ga(draft,"body","")    if draft else ""
                st.markdown(f"""
<div class="result-banner rb-success">
  <b>Response sent</b> to {ga(td,"customer_name")} ({ga(td,"customer_email")})
</div>""", unsafe_allow_html=True)
                st.markdown(f"""
<div class="email-wrap">
  <div class="email-header-row">
    <div class="email-subj">{d_subj}</div>
    <div class="email-to">To: {ga(td,"customer_name")} &lt;{ga(td,"customer_email")}&gt;</div>
  </div>
  <div class="email-body">{d_body}</div>
</div>""", unsafe_allow_html=True)
                if fb:
                    st.markdown(f'<div style="font-size:0.78rem;color:#6366f1;margin-top:0.5rem">Note appended: {fb}</div>', unsafe_allow_html=True)

            elif status == "escalated":
                team     = ga(esc,"escalation_team","tier2_support") if esc else "tier2_support"
                priority = ga(esc,"priority","normal") if esc else "normal"
                reason_e = ga(esc,"reason","")         if esc else ""
                sla      = SLA_MAP.get(priority,"24 hours")
                st.markdown(f"""
<div class="result-banner rb-warn">
  <b>Escalated</b> to {team.replace("_"," ").title()} — {priority} priority, {sla} SLA
  <div style="font-size:0.78rem;margin-top:4px;opacity:.85">{reason_e}</div>
</div>""", unsafe_allow_html=True)
                st.markdown(f"""
<div style="font-size:0.82rem;color:#44403c;line-height:2;padding:0.8rem 0">
Customer receives acknowledgement within 15 minutes.<br>
{team.replace("_"," ").title()} responds within {sla}.<br>
All call recordings and account history are attached to the case.<br>
Ticket status updated to In Progress in the dashboard.
</div>""", unsafe_allow_html=True)

        # ── Trace (collapsed) ─────────────────────────────────────
        trace = state.get("agent_trace", [])
        if trace:
            with st.expander("Agent trace"):
                for t in trace:
                    st.markdown(f'<div class="trace-line">-- {t}</div>', unsafe_allow_html=True)
