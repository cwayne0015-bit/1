# CLAUDE.md

Guidance for AI assistants working in this repository.

## What this is

A **digital-product sales site** built with **Jekyll** and deployed via
**GitHub Pages**. The product is "The Launch Playbook" — the page sells it,
takes payment through a Stripe Payment Link, and delivers the file on a
post-purchase page.

It also ships **CreatorsOS** (at `/app/`): a free, in-browser toolkit of three
creator tools (Revenue Goal Planner, Smart Pricing Lab, Launch Checklist). The
app is the top of the funnel — free tools that capture emails and upsell the
paid playbook. See "The CreatorsOS app" below.

It is a static site: no backend, no database, no JavaScript framework. Payment
and email capture are handled by third-party services (Stripe, Formspree).
JavaScript is plain vanilla and lives in two places only: `assets/js/creatoros.js`
(the app's tools) and a small inline pricing calculator inside the product
deliverable.

## Architecture & key files

The most important convention: **content lives in `_config.yml`, not in HTML.**
The page templates are thin and loop over data defined in config.

| Path | Role |
|------|------|
| `_config.yml` | Source of truth for **all** copy: product, features, stats, testimonials, FAQ, Stripe link, Formspree ID, download URL, **and the `app:` block** (CreatorsOS name/copy + the launch-checklist tasks). Edit content here. |
| `index.html` | The landing/sales page. Pure Liquid templating over `site.product`, `site.features`, `site.stats`, `site.testimonials`, `site.faq`. Uses the `default` layout. |
| `app.html` | **CreatorsOS** app at permalink `/app/`. Renders the three tools + the config-driven checklist, then loads `assets/js/creatoros.js`. Uses the `default` layout. |
| `assets/js/creatoros.js` | The app's logic. Pure calc functions (`revenuePlan`, `smartPrice`, `checklistProgress`, `roundPrice`) are exported for Node tests; DOM wiring at the bottom runs only in a browser. No dependencies, no framework. |
| `assets/js/creatoros.test.js` | Node unit tests for the calc functions (`node:test`, zero deps). **Excluded from the Jekyll build** so it never ships. |
| `success.html` | Post-purchase page at permalink `/success/`. Shows the download link (`site.product.download_url`). This is the Stripe checkout success URL. |
| `_layouts/default.html` | Base HTML shell. Includes nav + footer, emits `{% seo %}` (jekyll-seo-tag), links the stylesheet. |
| `_includes/nav.html`, `_includes/footer.html` | Shared header/footer partials, also config-driven. |
| `assets/css/style.css` | The entire stylesheet. Plain CSS (not SCSS), dark theme, CSS custom properties in `:root`. Served as-is. |
| `downloads/launch-playbook-x7k2.html` | The actual product deliverable — a self-contained HTML doc with inline CSS and an inline pricing-calculator script. Marked `noindex`. The obscured filename is intentional. |
| `robots.txt` | Disallows `/downloads/` and `/success/` from crawlers. |
| `Gemfile` | Pins `github-pages` gem (Jekyll + supported plugins) plus `webrick` for local preview. |
| `.github/workflows/build.yml` | CI that builds the site and verifies key pages were generated. |

## How the money flow works

1. Buyer clicks a CTA → goes to `site.product.stripe_payment_link` (a Stripe
   Payment Link configured in the Stripe dashboard).
2. Stripe's success URL is set to `https://YOURDOMAIN/success/` → renders
   `success.html`.
3. `success.html` surfaces `site.product.download_url`
   (`/downloads/launch-playbook-x7k2.html`).
4. Email capture (free-chapter offer) posts to Formspree via
   `site.formspree_id`.

**Security caveat already documented in `_config.yml`:** the download URL is
obscured and robots-excluded but **not access-controlled** — on a static host
anyone with the link can fetch it. Fine for low-ticket; for high-value goods,
deliver via Stripe/Gumroad/Lemon Squeezy instead. Don't represent the current
setup as truly gated.

## The CreatorsOS app (`/app/`)

A free, client-side toolkit that doubles as the funnel into the paid product.
Everything runs in the browser — there is no backend and no account system.

- **Three tools** (`app.html` + `assets/js/creatoros.js`):
  - *Revenue Goal Planner* — `revenuePlan(goal, price, conv, fee)` turns a
    monthly take-home goal into sales/month, /week, /day and (if a conversion
    rate is given) the traffic needed.
  - *Smart Pricing Lab* — `smartPrice(hours, rate, costs, targetProfit, sales, fee)`
    recommends a price from effort + costs + target, with a 6-month-recoup price
    floor so you never underprice.
  - *Launch Checklist* — tasks come from `site.app.checklist` in `_config.yml`;
    tick state is saved per-visitor in `localStorage` (key `creatoros.checklist.v1`),
    keyed by `data-task` (`<group-slug>-<index>`).
- **The funnel / "income" path** (honest version): the tools are a lead magnet.
  Free value → email capture (Formspree) + an upsell CTA to the Stripe link.
  Real revenue still requires a real Stripe Payment Link, a real Formspree form,
  and traffic — the code wires the plumbing, it doesn't conjure sales.
- **JS contract:** pure functions are pure and unit-tested; DOM wiring is guarded
  by `typeof document` and `typeof module` so the same file works in the browser
  and under Node. If you add an input/output, keep the element `id` in `app.html`
  in sync with the `id` strings in `creatoros.js`.

## Making changes

- **Copy / price / testimonials / FAQ / features** → edit `_config.yml` only.
  The HTML will pick it up automatically. Restart `jekyll serve` after editing
  `_config.yml` (Jekyll does not hot-reload config changes).
- **Layout / structure** → edit `index.html`, `success.html`, or the
  `_layouts` / `_includes` partials.
- **Styling** → edit `assets/css/style.css`. It is plain CSS; prefer the
  existing CSS custom properties (`--brand`, `--bg`, `--text`, etc.).
- **The product itself** → edit `downloads/launch-playbook-x7k2.html`.
- **App copy / checklist tasks** → edit the `app:` block in `_config.yml`.
- **App tool logic** → edit `assets/js/creatoros.js` and update
  `assets/js/creatoros.test.js` to match (keep element `id`s in sync with
  `app.html`).
- Use Jekyll's `relative_url` filter for internal links/assets so the site
  works under a `baseurl` subpath.
- `url` and `baseurl` in `_config.yml` are intentionally empty; set them for
  correct SEO/canonical URLs when a real domain is known.

## Local development

```bash
bundle install                 # first time
bundle exec jekyll serve       # http://localhost:4000
bundle exec jekyll build       # one-off build into _site/

node --test assets/js/creatoros.test.js   # run the app's unit tests (Node 18+)
```

`Gemfile.lock`, `_site/`, `vendor/`, and Jekyll caches are gitignored — do not
commit them. The JS tests use Node's built-in runner, so there is **no
`package.json` and nothing to `npm install`**.

> Sandbox note: some environments ship Bundler 4.x, where `bundle exec jekyll`
> can't see the transitive `jekyll` binstub. Run it directly with:
> `bundle exec ruby -e 'load Gem.bin_path("jekyll","jekyll")' -- build --strict_front_matter`.
> GitHub Actions uses Bundler 2.x, where `bundle exec jekyll` works normally.

## CI

`.github/workflows/build.yml` runs on push to `main` and `claude/**`, and on
PRs to `main`. It:

- Uses Ruby 3.3 with `bundler-cache`.
- Sets `LANG`/`LC_ALL=C.UTF-8` — **required**, because Jekyll's Sass converter
  fails under a non-UTF-8 locale. Keep these if you touch the workflow.
- Builds with `bundle exec jekyll build --trace --strict_front_matter`. The
  strict flag means **malformed/missing YAML front matter fails the build** —
  every `.html` page that should be processed needs valid front matter.
- Asserts `_site/index.html`, `_site/success/index.html`,
  `_site/app/index.html`, `_site/assets/css/style.css`, and
  `_site/assets/js/creatoros.js` exist (and that `creatoros.test.js` did **not**
  ship). If you rename/move these, update the workflow's checks too.
- A separate `test` job runs `node --test assets/js/creatoros.test.js` on Node 20.

Run `bundle exec jekyll build --strict_front_matter` and
`node --test assets/js/creatoros.test.js` locally before pushing to catch CI
failures early.

## Conventions & gotchas

- Prefer config-driven edits over hardcoding strings in templates.
- Every Liquid page needs front matter (`--- ... ---`) or Jekyll won't process
  it — and `--strict_front_matter` will fail CI on a malformed block.
- The deliverable in `downloads/` is deliberately standalone (inline CSS/JS, no
  dependence on the site theme) so it works when downloaded and opened offline.
  Keep it self-contained.
- Don't commit secrets. Stripe/Formspree are referenced only by public link/ID.
