---
name: money-finance
description: >-
  Revenue tracking, unit economics, and financial reports. Use when the user
  types /money-finance, wants to know if the business is actually profitable, or
  needs CAC/LTV/margin/runway numbers. Tracks revenue, computes unit economics,
  and produces a plain-language financial report.
---

# /money-finance — Financial Tracking

Tell the founder the truth about the money: what's coming in, what it costs, and
whether the math works.

## Core metrics

- **MRR / revenue** — recurring and one-time, trend over time.
- **Gross margin** — revenue minus cost of delivery (infra, fees, COGS).
- **CAC** — fully-loaded cost to acquire a paying customer.
- **LTV** — gross profit per customer over their lifetime.
- **LTV:CAC** — should comfortably clear 3:1 to scale paid acquisition.
- **Payback period** — months to recover CAC.
- **Churn** — logo and revenue churn.
- **Runway / burn** — if applicable.

## Workflow

1. **Pull the numbers** (Stripe/payments, ad spend, infra costs).
2. **Compute unit economics** and flag anything unhealthy (negative margin,
   payback too long, LTV:CAC below 3).
3. **Report in plain language** — what's working, what's leaking, the one number
   to fix next.
4. **Connect to action** — hand unhealthy CAC to `/money-ads`, weak conversion
   to `/money-diagnose`, etc.

## Value Quantification

- **Truth:** distinguishes real profit from revenue that doesn't cover costs.
- **Decision input:** LTV:CAC and payback gate whether to scale spend.
- **Plain language:** turns Stripe exports into one clear "fix this next".

## Rules

- Use fully-loaded costs — don't flatter CAC by excluding real spend.
- Surface the single most important number to fix, not a wall of metrics.
- Never call a business profitable on revenue alone — show margin.
