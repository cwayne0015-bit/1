# CLAUDE.md

Guidance for AI assistants working in the **wholesaling** workspace.

## What this is

A workspace for running a **real estate wholesaling** operation. Wholesaling is
the practice of getting a property under contract with a motivated seller, then
assigning that contract to a cash buyer for an assignment fee — without ever
taking title. The whole business is a pipeline:

```
Lead → Deal sourcing → Underwriting → Contract (seller) → Disposition (buyer) → Assignment → Close
```

This workspace organizes that pipeline into four specialized subagents, each
owning one stage. They live in `.claude/agents/` and are invoked
automatically by Claude Code when a task matches their `description`, or
explicitly by name.

## Subagents

| Agent | Stage | Owns |
|-------|-------|------|
| `deal-sourcing` | Lead gen & acquisition | Finding motivated sellers, building/qualifying lead lists, marketing channels, first contact, appointment setting. |
| `underwriting` | Deal analysis | ARV, repair estimates, comps, MAO (Maximum Allowable Offer), assignment-fee/profit modeling, go/no-go calls. |
| `buyer-relations` | Disposition | Cash-buyers list, matching deals to buyers, marketing the deal, negotiating the assignment fee. |
| `contracts` | Paperwork & close | Purchase & sale agreements, assignment contracts, disclosures, earnest money, title/escrow coordination. |
| `outreach` | Communication (cross-stage) | Talking to people: listing-agent/seller outreach, offer cover notes, call/text/email scripts, follow-up cadence, negotiation correspondence, scheduling, buyer/partner messaging. |

Each agent is a focused specialist with its own system prompt. Use the agent
that matches the pipeline stage; chain them for an end-to-end deal. `outreach`
is cross-cutting — it carries the messages the other agents generate, but never
sets price, drafts binding contract terms, or decides whether to buy.

## How a deal flows through the agents

1. **deal-sourcing** identifies a motivated seller and gathers property +
   seller context (condition, timeline, motivation, asking price, debt/liens).
2. **underwriting** runs the numbers — pulls comps, estimates ARV and repairs,
   computes the MAO, and confirms there's room for an assignment fee. Output is
   a go/no-go with a target offer price.
3. **contracts** papers the deal with the seller (purchase & sale agreement
   with an assignment clause, earnest money, inspection/contingency window).
4. **buyer-relations** markets the locked-up deal to the cash-buyers list,
   matches it to the right buyer, and negotiates the assignment fee.
5. **contracts** executes the assignment agreement and coordinates
   title/escrow to close. Wholesaler collects the assignment fee at closing.

## Conventions & guardrails

- **One stage, one agent.** Keep each agent's responsibilities scoped to its
  pipeline stage; don't have underwriting write contracts or sourcing run
  comps. Chain agents instead.
- **Numbers are conservative.** Underwriting should favor conservative ARV and
  generous repair estimates — a blown deal costs more than a passed one.
- **Not legal advice.** The `contracts` agent drafts and explains documents but
  is **not** a substitute for a licensed real estate attorney. State/local law
  on wholesaling, assignment, and required disclosures varies — some
  jurisdictions require a license or restrict assignment. Always flag where
  local counsel review is needed.
- **Disclose assignment.** Be transparent with sellers and buyers that the
  contract is assignable and that the wholesaler is not the end buyer. Hiding
  assignment intent is the fastest way to lose deals and invite legal trouble.
- **Verify, don't assume.** Comps, liens, title status, and buyer proof-of-funds
  should be verified, not taken on faith.

## Working in this repo

- Edit an agent's behavior by editing its file in `.claude/agents/`.
- Each agent file is Markdown with YAML front matter (`name`, `description`,
  and optional `tools`/`model`), followed by the system prompt body.
- Keep `description` fields action-oriented so Claude Code routes tasks to the
  right specialist automatically.
