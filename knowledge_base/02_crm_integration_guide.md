# CRM Integration Guide

## Overview
AutoVoice AI integrates with your dealership's CRM to sync call outcomes, log activities, update lead statuses, and push appointment data in real time.

## DealerSocket Integration

### Setup Steps
1. Log into your DealerSocket admin panel
2. Navigate to: Admin → API Settings → Third-Party Integrations
3. Generate a new API token with "Read/Write" permissions
4. Paste the token in AutoVoice dashboard: Settings → Integrations → DealerSocket
5. Click "Test Connection" — you should see a green checkmark within 30 seconds

### Common Issues
**Problem:** "Connection failed — invalid API token"
**Solution:** Regenerate the token in DealerSocket. Tokens expire every 90 days. Make sure you're copying the full token without trailing spaces.

**Problem:** Leads are not syncing to DealerSocket
**Solution:** Check that the "Lead Push" toggle is enabled in AutoVoice → Settings → Integrations. Also verify the DealerSocket user account has "Create Lead" permissions.

**Problem:** Duplicate leads appearing in CRM
**Solution:** Enable "Dedup by phone number" in AutoVoice integration settings. This matches incoming leads against existing CRM records by phone before creating new entries.

## VinSolutions Integration

### Setup Steps
1. In VinSolutions, go to Admin → API Management → New Application
2. Request scope: `leads:write`, `appointments:write`, `contacts:read`
3. Copy the Client ID and Client Secret
4. Enter both in AutoVoice: Settings → Integrations → VinSolutions
5. Authorize via OAuth — you'll be redirected to VinSolutions login

### Common Issues
**Problem:** OAuth token keeps expiring
**Solution:** AutoVoice refreshes tokens automatically every 55 minutes. If you're seeing expiry errors, check that your VinSolutions account has not had its password changed (this invalidates all OAuth tokens). Re-authorize from the integrations page.

**Problem:** Appointments not appearing in VinSolutions calendar
**Solution:** Verify the service advisor ID is correctly mapped in AutoVoice → Settings → Integrations → VinSolutions → Staff Mapping. Each advisor must be mapped individually.

## CDK Global Integration

### Setup Steps
1. Contact your CDK Global account representative to enable "CDK Drive API" access
2. CDK will provide: API endpoint URL, username, and password
3. Enter these in AutoVoice: Settings → Integrations → CDK Global
4. CDK integration uses a polling model (every 5 minutes) — not real-time

### Common Issues
**Problem:** CDK integration shows "Polling failed"
**Solution:** CDK servers have IP allowlist requirements. Contact AutoVoice support with your CDK endpoint URL — we will add our server IPs to your CDK allowlist.

## General CRM Troubleshooting
- All CRM sync errors are logged under: AutoVoice Dashboard → Reports → Integration Logs
- Logs are retained for 30 days
- If a sync fails, AutoVoice retries 3 times with exponential backoff before marking the event as "failed"
- Failed events can be manually re-synced from the Integration Logs page
