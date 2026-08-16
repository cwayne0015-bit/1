---
name: money-restore
description: >-
  Resume from a prior saved business state. Use when the user types
  /money-restore, returns to a project after a break, or asks to "pick up where
  we left off". Reads the latest checkpoint from ~/.smtm/sessions/{project}/ and
  rehydrates decisions, ruled-out paths, and the pending next action.
---

# /money-restore — Cross-session State Loader

Rebuild full working context from saved checkpoints so the session continues
seamlessly.

## Workflow

1. **Locate state.** Find `~/.smtm/sessions/{project}/`. If multiple projects
   exist, list them and let the user choose.
2. **Load the latest checkpoint** (via `latest.md` pointer, else newest
   `checkpoint-*.md`). Optionally replay earlier ones for full history.
3. **Summarize the rehydrated state** back to the user:
   - what's **Decided** (do not reopen these)
   - what's **Ruled out** (do not re-propose these)
   - **Open hypotheses** still in play
   - the pending **Next action**
4. **Hand off** to the appropriate skill to continue (e.g. `/money-strategy`,
   `/money-product`).

## Value Quantification

- **Zero re-work:** settled decisions are honored, not re-debated.
- **Speed:** full context restored in one step instead of re-explaining.
- **Safety:** ruled-out directions are not accidentally revived.

## Rules

- Treat **Decided** items as locked unless the user explicitly reopens them.
- Never silently contradict a ruled-out decision — flag it if you must.
- If no state exists, say so and route to `/money` for onboarding.
