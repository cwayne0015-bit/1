---
name: job-estimate
description: Use this skill when the user gives a rough, plain-English description of a job (contractor, handyman, freelance, or other service work) and wants a formatted estimate back — as structured JSON, a PDF, or both. Triggers on requests like "turn this into an estimate", "quote this job", "make me a PDF estimate for...", or a pasted job description followed by "how much would this run."
---

# Job Estimate Generator

Converts a rough text description of a job into a structured estimate
(JSON, and optionally a styled PDF/HTML) with line items, labor/materials
split, tax, and totals.

## Workflow

1. **Read the job description.** Pull out: who the client is (if mentioned),
   what the job is, where it is, and any rates, quantities, or prices the
   user already gave you.

2. **Break the work into line items.** Each line item needs a `category` of
   `labor`, `materials`, or `other` (permits, trip/dispatch fees, disposal,
   equipment rental, etc.), a `quantity` + `unit` (hr, ea, sq ft, ls for lump
   sum, ...), and a `unit_cost`.
   - If the user gave rates or prices, use them exactly.
   - If they didn't, estimate a reasonable market rate for the trade/region
     implied by the description, and say so explicitly in the `notes` field
     (e.g. "Labor rate assumed at $85/hr — confirm your actual rate").
   - Never silently invent a number without flagging it in `notes`. The
     point of `notes` is so the user can spot and correct every assumption
     before this goes to a client.

3. **Write the estimate JSON**, matching `schema.json` in this skill
   directory. Do NOT hand-compute `subtotal`, `tax_amount`, `total`, or each
   line item's `total` — leave them out or set to 0. `build_estimate.py`
   recomputes all of them deterministically from `quantity` × `unit_cost`,
   `tax_rate`, and `discount`, so the math is always correct even if your
   arithmetic isn't.
   - `estimate_number`: make one up if the user has no numbering scheme,
     e.g. `EST-<date>-0001`.
   - `tax_rate` is a percentage (`7` means 7%), omit or 0 if not taxable.
   - `business` fields are optional — leave blank/omit if the user hasn't
     told you their business name/contact info; don't fabricate a business
     identity.

4. **Install dependencies if needed** (first run in an environment only):
   ```bash
   pip install -r .claude/skills/job-estimate/requirements.txt --quiet
   ```

5. **Render the outputs** by running the build script on the JSON file you
   wrote:
   ```bash
   python3 .claude/skills/job-estimate/scripts/build_estimate.py path/to/estimate.json --out-dir path/to/output/dir
   ```
   This writes three files next to each other, named after
   `estimate_number`: a normalized `.json` (with totals filled in), a
   styled `.html` (good for a quick preview or emailing), and a `.pdf`
   (the client-facing deliverable). Use `--no-html` or `--no-pdf` to skip
   one if the user only asked for JSON.

6. **Report back.** Tell the user the total, flag anything you assumed
   (pull straight from what you put in `notes`), and point to the output
   file paths. If a PDF was generated, prefer sending it directly rather
   than just naming the path.

## Files in this skill

| File | Purpose |
|------|---------|
| `schema.json` | JSON Schema the estimate data must satisfy. Read this before drafting the JSON. |
| `scripts/build_estimate.py` | Validates the JSON (if `jsonschema` is installed), recomputes all totals, and renders HTML (Jinja2) + PDF (ReportLab). |
| `templates/estimate.html.j2` | HTML template used for the `.html` output. |
| `examples/sample_estimate.json` | A worked example (handyman job) showing the expected shape — use it as a reference, not a starting template to copy verbatim. |

## Notes

- Money math lives in `build_estimate.py`, not in your head — always run
  the script rather than reporting totals you computed yourself.
- If `reportlab`/`jinja2`/`jsonschema` aren't installed and `pip install`
  isn't possible in the current environment, still write the estimate JSON
  by hand matching `schema.json` — that alone satisfies a JSON-only request.
- This skill produces an *estimate*, not a binding invoice or contract. Keep
  the `terms` field honest about that (validity window, "prices may adjust
  once work begins," etc.) unless the user tells you otherwise.
