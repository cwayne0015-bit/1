#!/bin/bash
# SessionStart hook for creatorOS — runs at the start of Claude Code web sessions.
# creatorOS is a single static index.html (React via CDN, zero build), so there
# are NO dependencies to install. This hook just confirms the environment can
# serve and validate the app, and runs the structural smoke test.
set -euo pipefail

# Web-only: skip entirely in local CLI sessions.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

echo "creatorOS: static single-file app — no package install required."

if command -v node >/dev/null 2>&1; then
  node scripts/check.cjs
else
  echo "WARN: node not found; skipping structural smoke test." >&2
fi

if command -v python3 >/dev/null 2>&1; then
  echo "creatorOS: serve locally with  python3 -m http.server 8000  (open http://localhost:8000/)"
fi
