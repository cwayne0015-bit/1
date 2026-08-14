# CLAUDE.md

Guidance for AI assistants working in this repository.

## What this is

A single-product **digital-product sales site** built with **Jekyll** and
deployed via **GitHub Pages**. The product is "The Launch Playbook" — the page
sells it, and checkout + file delivery both happen on Gumroad.

It is a static site: no backend, no database, no JavaScript framework. Payment,
file delivery, and email capture are handled by third-party services (Gumroad,
Formspree). The only JavaScript anywhere is a small inline pricing calculator
inside the product deliverable itself.

## Architecture & key files

The most important convention: **content lives in `_config.yml`, not in HTML.**
The page templates are thin and loop over data defined in config.

| Path | Role |
|------|------|
| `_config.yml` | Source of truth for **all** copy: product name, price, features, stats, testimonials, FAQ, Gumroad product URL, Formspree ID. Edit content here. |
| `index.html` | The landing/sales page. Pure Liquid templating over `site.product`, `site.features`, `site.stats`, `site.testimonials`, `site.faq`. Uses the `default` layout. |
| `success.html` | Optional post-purchase thank-you page at permalink `/success/`, set as Gumroad's post-purchase redirect. Gumroad itself delivers the file (email + buyer library), so this page no longer surfaces a download link — it's just onboarding copy. |
| `_layouts/default.html` | Base HTML shell. Includes nav + footer, emits `{% seo %}` (jekyll-seo-tag), links the stylesheet. |
| `_includes/nav.html`, `_includes/footer.html` | Shared header/footer partials, also config-driven. |
| `assets/css/style.css` | The entire stylesheet. Plain CSS (not SCSS), dark theme, CSS custom properties in `:root`. Served as-is. |
| `downloads/launch-playbook-x7k2.html` | The master copy of the product deliverable — a self-contained HTML doc with inline CSS and an inline pricing-calculator script. **Uploaded to Gumroad as the product's file, and excluded from the Jekyll build** (see `exclude` in `_config.yml`) so it is never served from the site. Edit here, then re-upload to Gumroad. |
| `robots.txt` | Disallows `/success/` from crawlers. |
| `Gemfile` | Pins `github-pages` gem (Jekyll + supported plugins) plus `webrick` for local preview. |
| `.github/workflows/build.yml` | CI that builds the site and verifies key pages were generated. |

## How the money flow works

1. Buyer clicks a CTA → goes to `site.product.gumroad_url` (a Gumroad product
   page configured in the Gumroad dashboard, with
   `downloads/launch-playbook-x7k2.html` uploaded as its file).
2. Gumroad handles checkout, then emails the buyer their receipt + download
   link and adds the product to their Gumroad library — no file ever needs to
   be served from this site.
3. Gumroad's product can optionally be configured to redirect to
   `https://YOURDOMAIN/success/` after purchase, which renders `success.html`
   (a thank-you/onboarding page, not a download page).
4. Email capture (free-chapter offer) posts to Formspree via
   `site.formspree_id`.

Gumroad enforces its own access control on file delivery (buyers need a valid
purchase to reach their library/download link), which is stronger than the
static-host download-by-obscured-URL approach this site used previously — and
`downloads/` is now excluded from the build, so the deliverable is not served
from this site at all. `downloads/launch-playbook-x7k2.html` remains in the
repo only as the editable master copy; re-upload it to Gumroad whenever it
changes, or buyers keep getting the old version.

Note this protects the *published site*, not the repository: if this repo is
public on GitHub, the file is still readable there. Move it out of the repo if
that matters.

## Making changes

- **Copy / price / testimonials / FAQ / features** → edit `_config.yml` only.
  The HTML will pick it up automatically. Restart `jekyll serve` after editing
  `_config.yml` (Jekyll does not hot-reload config changes).
- **Layout / structure** → edit `index.html`, `success.html`, or the
  `_layouts` / `_includes` partials.
- **Styling** → edit `assets/css/style.css`. It is plain CSS; prefer the
  existing CSS custom properties (`--brand`, `--bg`, `--text`, etc.).
- **The product itself** → edit `downloads/launch-playbook-x7k2.html`.
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
  fails under a non-UTF-8 locale. Keep these if you touch the workflow.
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
- Don't commit secrets. Gumroad/Formspree are referenced only by public link/ID.
