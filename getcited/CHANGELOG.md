# Changelog

## v0.1.0 — 2026-06-03

### Added
- Weekly AI-search visibility engine: queries ChatGPT, Perplexity, and Gemini
  with the questions med-spa patients actually ask, detects whether the clinic
  is named vs. competitors, and computes a visibility score with week-over-week
  diffs.
- Auto-generated **Fix Kit** per clinic: FAQ block, schema.org JSON-LD
  (MedicalBusiness + FAQPage), Google Business Profile description + Q&A, and
  review-response templates — deterministic, no manual labor.
- Self-contained HTML report (email-friendly) rendered per clinic.
- Resend email delivery (optional; reports also saved to disk).
- Static landing page with SEO/GEO structured data and Stripe/Formspree
  placeholders ($149/mo, founding $99/mo).
- GitHub Actions weekly cron — free infra, no server to run.
- `--dry-run` mode that generates a realistic sample report with no API keys.
