# CLAUDE.md

Guidance for AI assistants working in this repository.

## What this is

A single-product **digital-product sales site** built with **Jekyll** and
deployed via **GitHub Pages**. The product is "The Launch Playbook" — the page
sells it, takes payment through a Stripe Payment Link, and delivers the file on
a post-purchase page.

It is a static site: no backend, no database, no JavaScript framework. Payment
and email capture are handled by third-party services (Stripe, Formspree). The
only JavaScript anywhere is a small inline pricing calculator inside the product
deliverable itself.

## Architecture & key files

The most important convention: **content lives in `_config.yml`, not in HTML.**
The page templates are thin and loop over data defined in config.

| Path | Role |
|------|------|
| `_config.yml` | Source of truth for **all** copy: product name, price, features, stats, testimonials, FAQ, Stripe link, Formspree ID, download URL. Edit content here. Also pins `plugins` (jekyll-seo-tag), `sass.style: compressed`, and `exclude`. |
| `index.html` | The landing/sales page. Pure Liquid templating over `site.product`, `site.features`, `site.stats`, `site.testimonials`, `site.faq`. Uses the `default` layout. Sections: hero + stats, "map problem" band, "Everything you get" feature grid, testimonials, `#get` pricing block, Formspree free-chapter capture, FAQ `<details>`, closing CTA. |
| `success.html` | Post-purchase page at permalink `/success/`. Shows the download link, but only renders the button when `site.product.download_url` is set and not `"#"`. This is the Stripe checkout success URL. |
| `_layouts/default.html` | Base HTML shell. Includes nav + footer, emits `{% seo %}` (jekyll-seo-tag), links the stylesheet. |
| `_includes/nav.html`, `_includes/footer.html` | Shared header/footer partials, also config-driven. |
| `assets/css/style.css` | The entire stylesheet. Plain CSS (not SCSS), dark theme, CSS custom properties in `:root`. Served as-is. |
| `downloads/launch-playbook-x7k2.html` | The actual product deliverable — a self-contained HTML doc with inline CSS and an inline pricing-calculator script. Marked `noindex`. The obscured filename is intentional. |
| `robots.txt` | Disallows `/downloads/` and `/success/` from crawlers. |
| `Gemfile` | Pins `github-pages` gem (Jekyll + supported plugins) plus `webrick` for local preview. |
| `.github/workflows/build.yml` | CI that builds the site and verifies key pages were generated. |

## How the money flow works

1. Buyer clicks a CTA → goes to `site.product.stripe_payment_link` (a Stripe
   Payment Link configured in the Stripe dashboard). **Until a real link is
   pasted in, this defaults to `"#get"`, an on-page anchor that scrolls to the
   pricing section** — so the CTAs work in preview without a live Stripe link.
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

**Placeholder values to replace before going live:**
`product.stripe_payment_link` (`"#get"`), `formspree_id` (`"your-form-id"`),
and `url`/`baseurl` (empty) are all placeholders. The site builds and previews
fine with them, but checkout, email capture, and canonical SEO URLs won't work
until they're set to real values.

## Making changes

- **Copy / price / testimonials / FAQ / features** → edit `_config.yml` only.
  The HTML will pick it up automatically. Restart `jekyll serve` after editing
  `_config.yml` (Jekyll does not hot-reload config changes).
- **Layout / structure** → edit `index.html`, `success.html`, or the
  `_layouts` / `_includes` partials.
- **Styling** → edit `assets/css/style.css`. It is plain CSS (dark theme);
  prefer the existing `:root` custom properties: `--bg`, `--bg-alt`, `--panel`,
  `--line`, `--text`, `--muted`, `--brand`, `--brand-2`, `--radius`, `--wrap`.
  Note the deliverable in `downloads/` has its own separate (light-theme) inline
  palette — don't conflate the two.
- **The product itself** → edit `downloads/launch-playbook-x7k2.html`. It is a
  full standalone playbook (30-day map table, copy-paste templates, a checklist,
  and a self-contained pricing calculator powered by a small inline `<script>`).
- Use Jekyll's `relative_url` filter for internal links/assets so the site
  works under a `baseurl` subpath.
- `url` and `baseurl` in `_config.yml` are intentionally empty; set them for
  correct SEO/canonical URLs when a real domain is known.

## Local development

```bash
bundle install                 # first time
bundle exec jekyll serve       # http://localhost:4000
bundle exec jekyll build       # one-off build into _site/
```

`Gemfile.lock`, `_site/`, `vendor/`, and Jekyll caches are gitignored — do not
commit them.

## CI

`.github/workflows/build.yml` runs on push to `main` and `claude/**`, and on
PRs to `main`. It:

- Uses Ruby 3.3 with `bundler-cache`.
- Sets `LANG`/`LC_ALL=C.UTF-8` — **required**, because Jekyll's Sass converter
  fails under a non-UTF-8 locale. Keep these if you touch the workflow. Also
  sets `JEKYLL_ENV=production`.
- Builds with `bundle exec jekyll build --trace --strict_front_matter`. The
  strict flag means **malformed/missing YAML front matter fails the build** —
  every `.html` page that should be processed needs valid front matter.
- Asserts `_site/index.html`, `_site/success/index.html`, and
  `_site/assets/css/style.css` exist. If you rename/move these, update the
  workflow's checks too.

Run `bundle exec jekyll build --strict_front_matter` locally before pushing to
catch CI failures early.

## Conventions & gotchas

- Prefer config-driven edits over hardcoding strings in templates.
- Every Liquid page needs front matter (`--- ... ---`) or Jekyll won't process
  it — and `--strict_front_matter` will fail CI on a malformed block.
- The deliverable in `downloads/` is deliberately standalone (inline CSS/JS, no
  dependence on the site theme) so it works when downloaded and opened offline.
  Keep it self-contained.
- Don't commit secrets. Stripe/Formspree are referenced only by public link/ID.
