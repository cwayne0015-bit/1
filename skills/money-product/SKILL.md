---
name: money-product
description: >-
  Build and ship an MVP end to end. Use when the user types /money-product, has
  a validated plan and wants to build, or needs to deploy a landing page, auth,
  and payments. Starts from a DESIGN.md design contract, builds, runs the ship
  lifecycle (VERSION + CHANGELOG + release notes), deploys, runs QA, and watches
  a post-deploy canary.
---

# /money-product — Product Build & Ship

Take a validated bet to a live, paid, monitored product — with a written design
contract up front so the build doesn't drift.

## Workflow

1. **DESIGN.md design contract.** Before code: write the contract — scope,
   user flows, data model, pages, payment flow, and explicit non-goals. Get the
   user's sign-off. This is the source of truth the build is checked against.
2. **Build the MVP.** Smallest thing that delivers the core value and can take
   money. Landing page → core feature → auth (if needed) → payments → SEO/GEO
   basics.
3. **Wire payments.** Stripe Payment Link / Checkout, success page, fulfillment.
   Be honest about what's truly gated vs. obscured.
4. **SEO / GEO baseline.** Titles, meta, structured data, sitemap, and
   AI-search-readable content.
5. **QA pass.** Hand off to `/money-quality` for the pre-launch gates, or run the
   core checks: critical flows, payment, mobile, error states.
6. **Ship lifecycle.** Bump `VERSION`, update `CHANGELOG.md`, write release
   notes. Tag the release.
7. **Deploy.**
8. **Post-deploy canary.** Watch the first traffic/transactions for errors,
   broken payments, or 500s. Define a rollback trigger before you deploy.

## Value Quantification

- **No drift:** DESIGN.md keeps the build anchored to the agreed scope.
- **Revenue-ready:** ships with working payments, not just a demo.
- **Safe launch:** canary + rollback trigger catch breakage in the first hour.

## Output

- Live URL, DESIGN.md, CHANGELOG entry, release notes
- Canary status + rollback trigger
- Tomorrow's first action: [specific task]

## Rules

- Write and confirm DESIGN.md before building.
- Ship the narrowest version that can take money; resist scope creep.
- Never deploy without a canary check and a defined rollback trigger.
