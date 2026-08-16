---
name: money-skillify
description: >-
  Codify a successful workflow into a project-local reusable skill. Use when the
  user types /money-skillify, has just completed a multi-step process worth
  repeating, or says "turn this into a skill". Produces a new SKILL.md the agent
  can invoke on future runs.
---

# /money-skillify — Workflow → Skill

When a workflow proves valuable, capture it as a reusable skill so it can be run
again deterministically instead of reconstructed from memory.

## Workflow

1. **Identify the workflow.** Review the steps the user just completed. Confirm
   the trigger ("when should this run?") and the outcome ("what does done look
   like?").
2. **Extract the reusable core.** Strip one-off specifics; keep the repeatable
   procedure, decision points, and quality bar.
3. **Write the SKILL.md** with valid frontmatter:
   - `name`: a clear `kebab-case` skill name
   - `description`: trigger conditions + what it does (third person)
   - body: numbered workflow, inputs, outputs, and rules
4. **Place it** project-locally (e.g. `.claude/skills/{name}/SKILL.md`) so it
   travels with the repo, or in `~/.claude/skills/` for global reuse.
5. **Verify** the description's trigger is specific enough to fire when needed.

## Value Quantification

- **Repeatability:** a proven process runs the same way every time.
- **Delegation:** the workflow becomes runnable by any agent, not just from memory.
- **Leverage:** one good run becomes infinite reuse.

## Rules

- Frontmatter `description` must state *when* to use the skill, not just what.
- Keep the body procedural and concrete; avoid vague advice.
- Prefer project-local skills unless the workflow is product-agnostic.
