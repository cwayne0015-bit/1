# Real Estate Wholesaling Business — Agent Team

## Business Overview
Operator: Christopher McGraw
Model: Zero-capital real estate wholesaling — locking up off-market deals under contract, then assigning the contract to a cash buyer for a fee. Construction background is the core edge: faster, more accurate repair-cost estimates than typical wholesalers.

Income streams:
1. Wholesale assignment fees
2. Construction consulting
3. Bird-dog referral network

## How This Agent Team Works
This main session is the orchestrator. It doesn't do the specialized work itself — it routes tasks to the right subagent below and stitches the results together.

| Stage | Subagent | Trigger |
|---|---|---|
| New lead comes in | `deal-sourcing` | Driving-for-dollars notes, skip trace results, bandit sign calls, REIA leads |
| Lead looks viable | `underwriting` | Run ARV, MAO, repair estimate |
| Deal numbers work | `buyer-relations` | Match to cash buyer list, draft outreach |
| Buyer found | `contracts` | Assignment paperwork, closing checklist |

## Daily Report Format
At the end of a working session, summarize:
- New leads added (count + source)
- Deals underwritten (address, ARV, MAO, repair estimate, go/no-go)
- Buyer matches made
- Contracts in progress / closing this week

## Standing Rules
- Always run MAO = (ARV × 0.70) − Repair Costs − Assignment Fee before quoting a number to a seller.
- Repair estimates default to Chris's construction-based judgment; flag anything outside the normal range for his review rather than guessing.
- Never send anything to a seller, buyer, or into contracts that commits to a number or legal term without Chris's explicit sign-off.
- This is not legal advice — `contracts` organizes and tracks paperwork; it does not replace an attorney or title company.
