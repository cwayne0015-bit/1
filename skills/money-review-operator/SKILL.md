---
name: money-review-operator
description: >-
  Solo-founder execution-feasibility review plus an architecture and data-flow
  stress test. Use when the user types /money-review-operator, asks "can one
  person actually build and run this?", or wants the plan checked for
  operational and technical realism. Judges scope against a solo founder's time
  and skills, and pressure-tests the system design.
---

# /money-review-operator — Operator Review

Review for the brutal reality of solo execution: can *one person* build, ship,
and operate this without drowning?

## What you evaluate

### Execution feasibility
- **Scope vs. time** — is the MVP shippable in weeks, not months, by one person?
- **Skill fit** — does the founder have (or can cheaply acquire) the skills?
- **Ongoing ops load** — support, moderation, fulfillment — does it scale with
  one operator, or does it cap at the founder's hours?
- **Dependencies** — third-party services that could break the business.

### Architecture & data-flow stress test
- **Data flow** — trace a request end to end; where can it fail or lose data?
- **State & persistence** — what must be durable; what happens on crash?
- **Failure modes** — payments, auth, webhooks, rate limits — graceful or fatal?
- **Cost at scale** — does infra cost stay sane as usage grows?

## Verdict

- **SHIP** — feasible solo, with the riskiest operational dependency named.
- **TRIM** — feasible only if scope is cut; name what to cut.
- **TOO BIG** — not a solo project as scoped; name why.

## Value Quantification

- **Realistic scope:** flags work that's secretly a team-sized effort.
- **Fewer outages:** stress-tests data flow and failure modes before launch.
- **Sustainable ops:** surfaces work that won't scale with one operator.

## Rules

- Assume one person with limited hours — no imaginary team.
- Trace at least one full request path end to end.
- If it can't ship solo, say so and propose the trimmed version.
