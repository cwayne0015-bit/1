---
name: money-panel
description: >-
  Run all four reviewers and synthesize their verdicts. Use when the user types
  /money-panel, wants a 360° second opinion before a big decision, or asks for a
  review board. Runs the investor, customer, operator, and skeptic reviews
  (plus optional `--add` custom personas), finds where they agree, and surfaces
  only the genuine taste decisions for the user to make.
---

# /money-panel — Review Panel

Convene the full review board, then do the hard part: separate consensus from
genuine disagreement so the user only spends judgment where it's needed.

## Workflow

1. **Run all four reviewers** on the current plan/product:
   - `/money-review-investor` — funding viability
   - `/money-review-customer` — willingness to pay
   - `/money-review-operator` — execution feasibility + architecture
   - `/money-review-skeptic` — red-team / failure modes
2. **Optional `--add <persona>`** — append custom reviewers (e.g. "--add
   compliance-officer", "--add power-user").
3. **Find agreement.** Collapse points all reviewers agree on into a short
   "settled" list — the user doesn't need to deliberate these.
4. **Surface taste decisions.** Where reviewers genuinely conflict, present each
   as a crisp either/or with the trade-off, for the user to decide.
5. **Recommend** a default for each taste decision, but make the call the user's.

## Value Quantification

- **Coverage:** four lenses (money, customer, builder, skeptic) in one pass.
- **Less deliberation:** consensus is settled automatically; only real forks reach the user.
- **Decision-ready:** conflicts arrive as crisp trade-offs, not raw opinions.

## Output

- **Settled** (unanimous) — short bullet list
- **Taste decisions** — each as a trade-off with a recommended default
- Tomorrow's first action: [specific task]

## Rules

- Don't make the user re-read four full reviews — synthesize.
- Only escalate *genuine* conflicts as taste decisions.
- Always recommend a default, but leave the final call to the user.
