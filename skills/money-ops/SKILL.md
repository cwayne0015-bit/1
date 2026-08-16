---
name: money-ops
description: >-
  24/7 autonomous operations with business health scoring and safety
  guardrails. Use when the user types /money-ops, wants to automate ongoing
  content/social/SEO/monitoring, or needs the business to run hands-off. Runs a
  health score, respects operating modes (open / staging / production), enforces
  an edit perimeter, and supports a panic stop.
---

# /money-ops — Autonomous Operations

Keep the business running and improving without the founder in the loop — safely.

## Operating modes

- **open** — experimentation; broad latitude, nothing live is at stake.
- **staging** — changes go to a non-production environment first.
- **production** — live revenue at stake; only whitelisted, reversible actions;
  destructive or irreversible actions require explicit human approval.

Always state the current mode before acting and act within its limits.

## Edit perimeter

Define, up front, exactly what the agent may touch (which files, channels,
accounts, budgets). Anything outside the perimeter requires the user to approve.
Never expand the perimeter silently.

## Business health score

On each run, compute a health snapshot:
- **Revenue** — trend vs. last period
- **Traffic** — sessions and source mix
- **Conversion** — visit → signup → paid
- **Reliability** — uptime, errors, failed payments
- **Pipeline** — content/outreach in flight

Flag any metric that crosses a threshold and propose the smallest corrective action.

## Canary monitoring

After any change, watch a canary window for regressions (errors, broken
payments, conversion drops). Roll back on a pre-defined trigger.

## Panic stop

If the user says "stop" / "panic" — halt all autonomous actions immediately,
make no further changes, and report current state.

## Value Quantification

- **Always-on:** routine ops and monitoring run without the founder present.
- **Bounded risk:** mode + edit perimeter cap blast radius; panic stop is instant.
- **Early warning:** health scoring + canary catch regressions before customers do.

## Rules

- State the operating mode and edit perimeter before acting.
- In production, irreversible actions require explicit human approval.
- Honor "stop"/"panic" immediately and unconditionally.
