# igkit — Instagram automation & monetization toolkit

A **ToS-compliant** Python toolkit for running an Instagram account:

- **AI content generation** — captions, hashtags, and post ideas (Anthropic API, structured output + prompt caching)
- **Post scheduling** — queue posts and auto-publish via the official Graph API
- **Monetization** — affiliate/product links + link-in-bio, a brand-deal media kit, and a sponsorship pipeline

## What this does and does not do

It uses **only** Instagram's official Graph API (Content Publishing + Insights).
It does **not** auto-like, mass follow/unfollow, comment-spam, generate fake
engagement, or scrape private endpoints. Those violate
[Instagram's Terms of Use](https://help.instagram.com/581066165581870) and
reliably get accounts permanently banned — which would destroy the very asset
you're trying to monetize.

## Requirements

- Python 3.10+
- An **Instagram Business or Creator account** linked to a Facebook Page
- A Meta app with the **Instagram Graph API** and permissions
  `instagram_content_publish` and `instagram_manage_insights`, plus a
  long-lived access token
- An Anthropic API key (for content generation)

Hosting note: the Graph API publishes from a **public media URL** — host your
images/videos somewhere reachable (S3, Cloudinary, a CDN) and pass the URL.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in the values
```

| Variable | Purpose |
| --- | --- |
| `ANTHROPIC_API_KEY` | AI content generation |
| `ANTHROPIC_MODEL` | Defaults to `claude-opus-4-7` |
| `CONTENT_EFFORT` | `low\|medium\|high\|max` — cost/quality knob (default `medium`) |
| `CONTENT_THINKING` | `on\|off` adaptive thinking (default `on`) |
| `IG_ACCESS_TOKEN` / `IG_USER_ID` | Graph API auth (the IG user is the Business account ID) |
| `IG_GRAPH_VERSION` | Graph API version (default `v21.0`) |
| `IGKIT_DB` | SQLite path (default `data/igkit.db`) |

## Usage

```bash
# 1. AI content generation (uses brand.example.json as the brand profile)
python -m igkit.cli content captions --brand brand.example.json --topic "new single-origin launch" --n 3
python -m igkit.cli content ideas    --brand brand.example.json --theme "behind the roastery" --n 5

# 2. Scheduling
python -m igkit.cli schedule add --at 2026-05-20T09:00:00+00:00 \
      --type image --media https://cdn.example/img.jpg --caption "Good morning ☕"
python -m igkit.cli schedule list
python -m igkit.cli schedule run     # publishes everything now due

# 3. Monetization
python -m igkit.cli links add --slug spring-roast --url https://shop.example/p/1 --type product --campaign spring
python -m igkit.cli links utm --url https://blog.example/post --campaign launch
python -m igkit.cli links bio --out bio.html        # static link-in-bio page
python -m igkit.cli mediakit --email me@example.com --rates '{"1 Reel":"$800","Story set":"$300"}' --out media_kit.md
python -m igkit.cli deals add --brand Acme --fee 1500 --deliverables "1 Reel + 2 Stories"
python -m igkit.cli deals list
```

### Scheduling without a daemon

`schedule run` publishes whatever is currently due and exits. Drive it on a
schedule with cron or a CI cron job — there is no long-running bot process:

```cron
*/15 * * * * cd /path/to/repo && /usr/bin/python -m igkit.cli schedule run >> data/run.log 2>&1
```

## How AI content generation is built

- **Structured output**: `client.messages.parse(output_format=...)` returns
  validated Pydantic objects (`ContentPackage`, `IdeaList`).
- **Prompt caching**: the brand profile + instructions are a *stable* prefix
  placed in `system` with a `cache_control` breakpoint; the per-request topic
  goes in the user turn after it, so the cached prefix stays byte-stable
  across calls for the same brand. (Short brand prompts may fall under the
  model's minimum cacheable prefix and simply won't cache — no error.)
- **Adaptive thinking** with a configurable `effort` level balances quality
  against cost for high-volume generation.

## Tests

```bash
pytest -q
```

Tests cover the offline logic (UTM building, scheduler queue, link registry,
deal pipeline, brand profile). Graph API and Anthropic calls are not exercised
in tests — run them against your own credentials.
