---
name: money-upgrade
description: >-
  Auto-update the Show Me The Money skill suite. Use when the user types
  /money-upgrade, asks to update the skills, or wants to know if a newer version
  exists. Checks npm for the latest version, downloads and replaces local
  skills, reads the CHANGELOG, and prompts to restart.
---

# /money-upgrade — Version Management

Keep the installed skills current with the published npm package.

## Workflow

1. **Read the installed version** from the local package metadata.
2. **Check npm** for the latest published version of
   `@orrisai/show-me-the-money`.
3. **Compare.** If already current, say so and stop. If behind, list the version
   delta.
4. **Update** by re-running the installer:
   ```bash
   npx @orrisai/show-me-the-money
   ```
   This downloads the latest skills and replaces the local copies in
   `~/.claude/skills/`.
5. **Read the CHANGELOG** for the new versions and summarize what changed for
   the user.
6. **Prompt to restart** the agent / reload plugins so the new skills load:
   ```bash
   claude plugin update money@show-me-the-money
   /reload-plugins
   ```

## Value Quantification

- **Current:** always running the latest frameworks and fixes.
- **Transparent:** CHANGELOG summary explains what changed before you adopt it.
- **One step:** check, download, replace, and reload in a single flow.

## Rules

- Never partially update — replace the full skill set to avoid version drift.
- Always surface the CHANGELOG highlights, not just the version number.
- Remind the user a restart / reload is required for changes to take effect.
