# TCPA Compliance & Legal Guide

## What is TCPA?
The Telephone Consumer Protection Act (TCPA) is a US federal law that restricts unsolicited telemarketing calls, auto-dialed calls, pre-recorded messages, and text messages. Violations can result in fines of $500–$1,500 per call/message.

## AutoVoice AI and TCPA Compliance

### Inbound Calls
Inbound calls are TCPA-compliant by nature — the customer initiates the call. No special action required.

### Outbound Calls (ProActive Dialer)
For outbound calling, you MUST ensure:
1. **Prior express written consent** — You have documented proof the customer consented to receive automated calls/texts from your dealership
2. The number is NOT on the National Do Not Call (DNC) Registry
3. Calls are made only between **8:00 AM and 9:00 PM** in the recipient's local time zone

AutoVoice AI automatically:
- Scrubs numbers against the National DNC Registry (updated daily)
- Enforces calling hour restrictions based on area code → time zone mapping
- Plays a required disclosure at the start of each outbound call: "This call may be recorded..."

### SMS Compliance
- AutoVoice AI processes all opt-out keywords: STOP, UNSUBSCRIBE, CANCEL, END, QUIT
- Opt-outs are processed within 10 minutes and synced to your CRM
- After opt-out, no further SMS will be sent to that number
- Opt-in keywords: START, YES, SUBSCRIBE — customers can re-opt-in at any time

## Consent Management
AutoVoice AI maintains a Consent Log for all contacts:
- **Location:** Dashboard → Compliance → Consent Log
- **Fields logged:** Phone number, consent type, consent source, timestamp, IP address (for web forms)
- Consent records are retained for 5 years as required by TCPA regulations

## Call Recording Consent
AutoVoice AI records all calls by default for quality assurance.
- **All-party consent states** (California, Florida, Illinois, Pennsylvania, etc.): The AI plays a disclosure at call start: "This call is being recorded for quality purposes."
- **One-party consent states:** Recording proceeds without explicit disclosure (though disclosure is still recommended)
- Recording can be disabled in Settings → Voice → Call Recording

## Do Not Call (DNC) Management
AutoVoice AI maintains both:
1. **National DNC Registry** — Updated daily. Numbers on this list cannot receive unsolicited outbound calls.
2. **Internal DNC List** — Your dealership-specific DNC list. Add numbers manually via Dashboard → Compliance → DNC List or via CRM sync.

When a customer says "stop calling me" or "remove me from your list" during a call, AutoVoice AI automatically:
- Adds the number to your internal DNC list
- Logs the request with timestamp
- Notifies your CRM via the integration

## Escalation for Legal/Compliance Issues
If a customer threatens legal action, mentions a lawyer, or cites TCPA specifically:
- **AutoVoice AI will immediately escalate this call to a human operator**
- A compliance alert is sent to your account's designated compliance contact email
- The call recording is flagged and retained regardless of your recording settings

## What AutoVoice AI Does NOT Handle
- AutoVoice AI does not provide legal advice
- It is the dealership's responsibility to obtain and document prior express written consent
- For TCPA audits or disputes, contact a qualified telecommunications attorney
- AutoVoice AI will provide compliance logs and call recordings upon request for legal proceedings

## Compliance Contacts
- For compliance questions: compliance@autovoiceai.com
- For urgent legal escalations: Call our compliance hotline at 1-800-AV-LEGAL (available 24/7)
