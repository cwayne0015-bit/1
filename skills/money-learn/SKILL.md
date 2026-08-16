---
name: money-learn
description: >-
  Manage atomic project learnings plus portfolio learnings shared across every
  project. Use when the user types /money-learn, discovers something worth
  remembering (a tactic that worked, a channel that failed), or wants to apply
  lessons from past projects to a new one.
---

# /money-learn — Learnings Knowledge Base

Capture reusable lessons as small, atomic, reusable units — and promote the ones
that generalize across projects.

## Two scopes

- **Project learnings** — specific to the current project. Stored under
  `~/.smtm/sessions/{project}/learnings/`.
- **Portfolio learnings** — patterns that hold across *all* projects (e.g.
  "Reddit launches convert better than Product Hunt for dev tools"). Stored
  under `~/.smtm/learnings/`. These are surfaced in every future project.

## Workflow

1. **Capture as an atom.** One learning = one claim + the evidence + the action
   it implies. Keep it small and self-contained.
2. **Classify scope.** Project-specific or portfolio-wide? When in doubt, start
   project-local and promote later.
3. **Promote** repeated project learnings into portfolio learnings when the same
   lesson recurs across two or more projects.
4. **Surface relevant atoms** at the start of related work in other skills.

## Atom template

```markdown
- **Learning:** <one-sentence claim>
  - **Evidence:** <what happened / data>
  - **Implies:** <what to do differently next time>
  - **Scope:** project | portfolio
```

## Value Quantification

- **Compounding:** lessons from one product accelerate the next.
- **No repeated mistakes:** failed channels/tactics are recorded once.
- **Atomic recall:** small units are easy to match to new situations.

## Rules

- One claim per atom — keep them small and composable.
- Always pair a learning with the action it implies.
- Promote to portfolio only when a pattern recurs.
