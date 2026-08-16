---
name: money-save
description: >-
  Checkpoint the current business state to disk so it survives across sessions.
  Use when the user types /money-save, finishes a decision worth keeping (wedge,
  pricing, GTM plan), or before ending a session. Writes an append-only
  timestamped checkpoint to ~/.smtm/sessions/{project}/.
---

# /money-save — Cross-session Checkpoint

Persist what was decided so a future session (or a different agent) can resume
without re-litigating settled questions.

## Workflow

1. **Identify the project slug.** Derive a stable `{project}` slug from the
   product name. Create `~/.smtm/sessions/{project}/` if absent.
2. **Snapshot the live state** into a single markdown checkpoint:
   - **Decided:** locked decisions (wedge, pricing, stack, positioning)
   - **Ruled out:** directions explicitly abandoned, with the reason
   - **Open hypotheses:** things still being tested
   - **Next action:** the single tomorrow-shippable task
3. **Write append-only.** Name the file `checkpoint-{YYYYMMDD-HHMMSS}.md`.
   Never overwrite a previous checkpoint — history is the point.
4. **Update `latest.md`** as a pointer to the newest checkpoint for fast restore.

## Checkpoint template

```markdown
# Checkpoint — {project} — {timestamp}
## Decided
- ...
## Ruled out
- ... (because ...)
## Open hypotheses
- ...
## Next action
- Tomorrow's first action: ...
```

## Value Quantification

- **Memory:** decisions and dead-ends survive context loss — no re-deciding.
- **Continuity:** any future session resumes from the exact last state.
- **Auditability:** append-only history shows how the business evolved.

## Rules

- Append, never overwrite. Every checkpoint is immutable.
- Capture *reasons* for ruled-out paths, not just the conclusion.
- Confirm the project slug with the user when ambiguous.
