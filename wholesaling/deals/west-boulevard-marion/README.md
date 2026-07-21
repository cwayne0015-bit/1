# West Boulevard, Marion — Cash-Buyer Batch Call Campaign

Automates outbound disposition calls to the cash-buyers list via an
ElevenLabs Conversational AI agent, using `batch_call_campaign.py` (buyer
disclosure/outreach content owned by the `outreach` agent; recipient
list/tiering owned by `buyer-relations`).

## Property (dynamic variables baked into the script)

3/1, ~1,150 sqft, built 1962. Repair scope: full bath, kitchen, roof, HVAC.
ARV ~$135K–$145K. Ask $72,000 cash, as-is. 14-day close.
*Planning estimates only — not an appraisal or a warranty.*

## Setup

```bash
pip install -r requirements.txt
export ELEVENLABS_API_KEY=...
export ELEVENLABS_AGENT_ID=agent_8701ky1adxzxf8cacq28h8pba1fv
export ELEVENLABS_PHONE_NUMBER_ID=...   # the imported Twilio number
python batch_call_campaign.py buyers.csv
```

`buyers.csv` columns: `phone_number,buyer_name,buyer_company,line_type,consent_on_file,dnc,last_called`.

## Compliance guardrails already built into the script — do not remove

- **DNC first.** Any row with `dnc` set is dropped before anything else.
- **Tier gating.** Only calls landline/VOIP-business lines (Tier A) or
  numbers with `consent_on_file` (Tier B). Everything else (Tier C — mobile
  numbers with no consent on file) is dropped, not called.
- **Cooldown.** Skips anyone called in the last 48 hours.
- **Call window.** Only schedules the next weekday at 10:00 AM
  America/Chicago — never nights or weekends.
- **First-run cap.** Caps the first batch at 25 recipients so a human can
  listen to the agent before scaling up, and requires an interactive `y`
  confirmation before submitting.

These exist to satisfy the same TCPA / FTSA (Florida Telephone Solicitation
Act, if calling into FL) / general telemarketing-consent obligations that
`outreach.md` and `buyer-relations.md` already hold this workspace to. If you
extend this script (new markets, higher concurrency, different call
windows), keep DNC/tiering/cooldown/window logic intact and get counsel
review before calling into a new jurisdiction with its own telemarketing
statute. **This is not legal advice.**

Before running for real: verify the buyer's proof-of-funds status still
belongs in a Tier A/B campaign, and that the agent script it runs discloses
the caller as an investor and the contract's assignability, per
`outreach.md`'s honest-disclosure guardrail.
