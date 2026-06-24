# Call Quality Troubleshooting Guide

## Understanding Call Quality Metrics
AutoVoice AI measures call quality using several key metrics:
- **Transcription Accuracy Rate (TAR):** % of words correctly transcribed (target: >95%)
- **Intent Recognition Rate (IRR):** % of turns where AI correctly identified intent (target: >90%)
- **Escalation Rate:** % of calls handed off to a human (target: <20% for standard queries)
- **Call Completion Rate (CCR):** % of calls resolved without abandonment (target: >85%)

You can view these in: AutoVoice Dashboard → Analytics → Call Quality

## Common Call Quality Issues

### Issue: AI is not understanding customers / misinterpreting requests
**Symptoms:** Customers report AI giving wrong answers, repeating itself, or saying "I didn't understand that"

**Causes and Fixes:**
1. **Background noise:** If the dealership floor is noisy, enable "Noise Cancellation" in Settings → Voice → Audio Processing
2. **Accent or dialect issues:** Submit 5–10 example call recordings via support. Our team retrains the model on your dealership's specific customer base within 5 business days
3. **Script gaps:** The AI may not have been trained on certain question types. Go to Settings → Script Builder → Unknown Intents to see what customers are asking that isn't covered. Add new intents and responses there
4. **Low audio quality:** Check if your phone carrier is transcoding audio to a lower bitrate. We recommend using a SIP trunk with G.711 codec for best quality

### Issue: Calls are dropping unexpectedly
**Symptoms:** Calls end mid-conversation, customer complains of being disconnected

**Causes and Fixes:**
1. **SIP timeout:** If silence lasts more than 30 seconds (default), the call is terminated. Adjust in Settings → Voice → Silence Timeout
2. **DTMF (keypad) issues:** Some phone systems conflict with our DTMF detection. Disable "DTMF Detection" in Settings → Voice if customers use phone menus
3. **Carrier-level drops:** Run a call quality test from AutoVoice Dashboard → Diagnostics → Call Test. If packet loss exceeds 2%, contact your VoIP carrier

### Issue: AI giving outdated inventory information
**Symptoms:** AI tells customer a car is available when it's already sold

**Fix:** Enable "Live Inventory Sync" in Settings → Integrations. This syncs inventory from your DMS every 15 minutes. If your DMS is not supported, you can upload a daily inventory CSV via Settings → Inventory → Manual Upload

### Issue: Long pauses or slow AI responses
**Symptoms:** Noticeable delay (>2 seconds) before AI responds

**Causes and Fixes:**
1. **Model latency:** Switch to "Turbo Mode" in Settings → Voice → Response Speed (uses a faster model, slightly lower accuracy)
2. **Network latency:** The AutoVoice server closest to your dealership is automatically selected, but you can manually override in Settings → Infrastructure → Region
3. **Complex queries:** If a customer asks a multi-part question, AI processing takes longer. This is expected behavior

### Issue: AI answering calls in the wrong language
**Fix:** Set the primary and secondary languages in Settings → Voice → Language. We support English, Spanish (US), and French (Canadian). Multilingual auto-detection is available on Growth and Enterprise plans.

## Escalation Behavior
The AI will automatically escalate a call to a live agent when:
- Customer says "agent," "human," "representative," or "operator"
- Confidence score drops below the threshold set in Settings → Voice → Escalation Threshold (default: 60%)
- The query type is marked as "always escalate" in the script builder (e.g., financing applications, trade-in appraisals)
- The call has been transferred more than 2 times already

## Requesting a Call Quality Review
For persistent quality issues, submit a support ticket with:
- At least 3 example call recordings or call IDs
- Description of the problem
- Dealership name and AutoVoice account ID
Our quality team will respond within 2 business days with a detailed analysis.
