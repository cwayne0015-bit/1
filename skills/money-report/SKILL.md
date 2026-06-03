---
name: money-report
description: >-
  Merge all saved checkpoints into a single shareable deliverable report. Use
  when the user types /money-report, wants a summary to share with a co-founder
  or investor, or needs to see multi-week/month progress in one place. Reads
  every checkpoint in ~/.smtm/sessions/{project}/ and writes a timestamped
  report to ~/.smtm/reports/{project}/.
---

# /money-report — Deliverable Report Generator

Compress a project's entire saved history into one clean markdown document a
human can read end to end.

## Workflow

1. **Gather** all `checkpoint-*.md` files for the project, in chronological
   order.
2. **Synthesize**, do not just concatenate:
   - **Executive summary** — what the business is, current stage, revenue
   - **Decision timeline** — key decisions in the order they were made
   - **What was ruled out** — and why (saves the reader the same dead-ends)
   - **Current open questions** — live hypotheses
   - **Recommended next actions** — prioritized
3. **Write** to `~/.smtm/reports/{project}/report-{YYYYMMDD-HHMMSS}.md`.
   Never overwrite — reports are timestamped snapshots.
4. **Surface the path** and offer to tailor a version for a specific audience
   (co-founder, investor, advisor).

## Value Quantification

- **Shareable:** turns months of session state into one document to hand off.
- **Narrative:** shows the *reasoning path*, not just the current state.
- **Immutable:** timestamped reports never clobber earlier ones.

## Rules

- Synthesize for a reader who wasn't in any session.
- Preserve the reasoning behind ruled-out paths.
- Reports are read-only artifacts; never overwrite a prior report.
