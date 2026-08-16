---
name: money-quality
description: >-
  Pre-launch quality gates. Use when the user types /money-quality, is about to
  ship, or wants code review, security, performance, and accessibility checks.
  Runs code review, an OWASP + STRIDE security audit, performance checks, and
  accessibility review — and includes a tech-triage debugging mode for live
  issues.
---

# /money-quality — Quality Gates

The checkpoint between "it works on my machine" and "it's safe to charge people
on it."

## Pre-launch gates

1. **Code review** — correctness bugs, error handling, dead code, secrets in the
   repo, missing validation.
2. **Security — OWASP Top 10** — injection, broken auth, broken access control,
   misconfig, sensitive data exposure, SSRF, etc.
3. **Security — STRIDE threat model** — Spoofing, Tampering, Repudiation,
   Information disclosure, Denial of service, Elevation of privilege. Walk each
   against the system's trust boundaries.
4. **Performance** — page weight, key queries, N+1s, cold-start, payload sizes,
   caching.
5. **Accessibility** — semantic markup, contrast, keyboard nav, alt text, labels.

Each gate returns **PASS / FIX-BEFORE-LAUNCH / FIX-LATER** with specifics.

## Tech-triage debugging mode

When invoked on a live bug: reproduce → isolate the failing layer → form one
hypothesis → cheapest test to confirm → fix → verify → add a guard so it can't
silently recur.

## Value Quantification

- **Trust:** payment and auth paths are audited before real money flows.
- **Prioritized:** findings are bucketed by must-fix vs. later, not a flat list.
- **Defensible:** STRIDE forces threat coverage, not just a lint pass.

## Rules

- Treat anything touching payments, auth, or PII as launch-blocking until proven safe.
- Give every finding a severity and a concrete fix.
- Never report "looks fine" without having checked the trust boundaries.
