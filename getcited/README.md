# GetCited

**Get your med spa recommended by AI.** Every week, GetCited asks ChatGPT,
Perplexity, and Gemini the questions patients actually ask, reports whether your
clinic is recommended (vs. competitors), and generates a **Fix Kit** — the FAQ,
schema markup, Google Business Profile copy, and review replies that get you
cited. Next week's report shows your movement.

Built to run on **free infrastructure** with **no server to babysit** and
**zero npm dependencies** (Node 18+ built-ins only).

---

## What's in here

```
getcited/
├─ site/index.html          ← the landing page (deploy this anywhere static)
├─ src/                     ← the report engine
│   ├─ run.js               ← entry point (weekly job)
│   ├─ providers.js         ← ChatGPT / Gemini / Perplexity calls
│   ├─ analyze.js           ← did AI name you? vs. competitors + diffs
│   ├─ fixkit.js            ← generates the Fix Kit (schema, FAQ, GBP, reviews)
│   ├─ report.js            ← renders the HTML report
│   └─ email.js             ← sends via Resend
├─ config/clinics.example.json  ← copy → clinics.json and edit
├─ samples/                 ← a generated sample report (made with --dry-run)
└─ .github/workflows/getcited-weekly.yml  ← (lives at repo root) weekly cron
```

---

## See a sample right now (no keys needed)

```bash
cd getcited
node src/run.js --dry-run --config config/clinics.example.json --out samples
open samples/glow-aesthetics-austin.html
```

This simulates the "you're invisible, competitors get named" state and shows the
full report + Fix Kit. Use it as your pre-sale asset.

---

## Go live in 3 steps

You can launch with **just an OpenAI key** and **no email** (reports save to
`out/`). Add the rest when ready.

### 1. Get your keys (free tiers exist for all)

| Key | Where | Needed for |
|---|---|---|
| `OPENAI_API_KEY` | platform.openai.com/api-keys | checking ChatGPT (min. one provider) |
| `GEMINI_API_KEY` | aistudio.google.com/app/apikey | checking Gemini (optional) |
| `PERPLEXITY_API_KEY` | perplexity.ai/settings/api | checking Perplexity (optional) |
| `RESEND_API_KEY` + `REPORT_FROM` | resend.com | emailing reports (optional) |

Local: `cp .env.example .env` and fill it in.
Production: add each as a **GitHub Actions secret**
(repo → Settings → Secrets and variables → Actions).

### 2. Add your clinics

```bash
cp config/clinics.example.json config/clinics.json
# edit: clinic name, city, website, email, treatments, competitors
```

### 3. Run it

```bash
node src/run.js          # checks every clinic, writes reports, emails them
```

The weekly cron (`.github/workflows/getcited-weekly.yml`) does this every Monday
automatically once your secrets are set — **no server required.** You can also
trigger it manually from the repo's **Actions** tab.

---

## Take payment

The landing page (`site/index.html`) has two Stripe buttons and a free-sample
form. To wire them up (no code):

1. Create two **Stripe Payment Links** (dashboard.stripe.com/payment-links):
   `$99/mo` (founding) and `$149/mo`.
2. In `site/index.html`, replace the two `href="#"` values marked
   `<!-- SETUP -->` with those links.
3. Create a free **Formspree** form and replace `YOUR_FORM_ID` in the sample
   form's `action`.
4. Deploy `site/` to any static host (Netlify, Vercel, GitHub Pages, Cloudflare
   Pages — all free).

---

## Deploy the landing page

It's a single static file. Easiest options:

- **Netlify / Cloudflare Pages / Vercel**: drag-and-drop the `site/` folder.
- **GitHub Pages**: serve the `getcited/site` directory.

No build step.

---

## How "the cure" works (honest version)

AI assistants weight **structured data (JSON-LD)**, **FAQ/Q&A content**, and
**Google Business Profile** signals when recommending local businesses. The Fix
Kit generates exactly those, tailored to your clinic. Publishing them makes you
more likely to be cited — but it's an emerging channel and **not a guarantee**.
Sell it as optimization with weekly proof, never as guaranteed rankings.

---

## Roadmap (post-MVP)

- One-click publish to Google Business Profile via API
- Per-clinic web dashboard (currently: emailed report + Supabase/Stripe later)
- Expand verticals (dentists, law firms, real-estate) — same engine, new prompts
