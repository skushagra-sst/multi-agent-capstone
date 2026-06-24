# Onboarding Guide — Getting Started with AutoVoice AI

## Onboarding Overview
Welcome to AutoVoice AI! This guide walks you through the complete setup process to get your dealership's AI voice and text agent live.

## Step 1: Account Setup (Day 1)
1. You will receive a welcome email with your AutoVoice Dashboard login credentials
2. Log in at: dashboard.autovoiceai.com
3. Complete your dealership profile: Settings → Dealership → Profile
   - Dealership name, address, time zone, business hours
   - Primary contact and billing contact
   - Dealership group name (if part of a multi-location group)

## Step 2: Phone Number Setup (Day 1–2)
Two options:
- **Port your existing number:** Transfer your current dealership phone number to AutoVoice. This takes 5–10 business days. Submit port request via Settings → Phone Numbers → Port Number
- **Get a new number:** AutoVoice provides a local or toll-free number instantly. Go to Settings → Phone Numbers → Add Number

Call forwarding setup (for porting):
- During the porting window, set conditional call forwarding on your existing number to forward to your AutoVoice number
- Instructions for major carriers are in Settings → Phone Numbers → Forwarding Instructions

## Step 3: Script Configuration (Day 2–3)
This is the most important step — configuring how your AI agent speaks and responds.

1. Go to: Settings → Script Builder
2. Start with a template: "Service Department," "Sales Floor," or "General Dealership"
3. Customize:
   - **Greeting:** How the AI answers ("Thank you for calling [Dealership Name], this is AVA, your AI assistant...")
   - **Intents:** What questions the AI can handle (appointments, hours, directions, inventory, financing)
   - **Escalation Triggers:** When to hand off to a human
   - **After-hours behavior:** Voicemail or appointment booking only
4. Use "Preview Mode" to test responses before going live

## Step 4: CRM Integration (Day 3–4)
See the CRM Integration Guide for detailed setup steps for your specific CRM.

After CRM is connected, configure field mapping:
- Settings → Integrations → [Your CRM] → Field Mapping
- Map AutoVoice fields (caller name, phone, intent, appointment date) to your CRM fields

## Step 5: Test Calls (Day 4–5)
Before going live, run 10–15 test calls covering:
- Standard appointment booking
- Hours and directions inquiry
- Escalation to human
- After-hours scenario
- Unknown/out-of-scope question

Test call instructions: Dashboard → Diagnostics → Test Calls

## Step 6: Go Live (Day 5–7)
1. AutoVoice team reviews your configuration (within 24 hours)
2. Approval email sent with "Go Live" checklist
3. Complete the checklist (verify forwarding, test one final call)
4. Click "Go Live" in Dashboard → Settings → Status
5. Your AI agent begins answering calls immediately

## Step 7: Post-Launch (Week 2 onward)
- Review call quality metrics daily for the first 2 weeks: Dashboard → Analytics → Call Quality
- Add missing intents as you discover gaps: Settings → Script Builder → Unknown Intents
- Review escalation logs to understand which call types need script improvement

## Onboarding Support
- Dedicated onboarding specialist assigned to every new account
- Email your specialist directly (name in welcome email)
- Express onboarding available for $299 (2–3 day turnaround)
- Group onboarding webinars: Every Tuesday at 2 PM ET (register at autovoiceai.com/webinar)

## Common Onboarding Questions

**Q: Can I use my existing toll-free number?**
A: Yes — number porting supports toll-free numbers. Porting timeline is the same (5–10 business days).

**Q: What if my CRM is not on the supported list?**
A: We support custom integrations via Webhooks and Zapier. Contact your onboarding specialist to set this up.

**Q: Can I have different scripts for different departments (sales vs. service)?**
A: Yes. Each phone number in your account can have its own script. Create a separate number for each department in Settings → Phone Numbers.
