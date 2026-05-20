"""Affiliate / product link tooling: UTM tagging, a link registry, and a
link-in-bio page export. Covers the 'affiliate marketing' and 'sell products'
monetization paths.

Click attribution is intentionally done with UTM parameters (handled by your
analytics, e.g. GA4) rather than a custom redirect tracker, so there is no
server to run and nothing that touches Instagram's platform.
"""

from __future__ import annotations

import html
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

LINK_TYPES = {"affiliate", "product", "content", "other"}


def build_utm_url(
    base_url: str,
    *,
    source: str = "instagram",
    medium: str = "social",
    campaign: str | None = None,
    content: str | None = None,
    term: str | None = None,
) -> str:
    """Append UTM params to a URL, preserving any existing query string."""
    parts = urlparse(base_url)
    if not parts.scheme or not parts.netloc:
        raise ValueError(f"Not an absolute URL: {base_url!r}")
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["utm_source"] = source
    query["utm_medium"] = medium
    if campaign:
        query["utm_campaign"] = campaign
    if content:
        query["utm_content"] = content
    if term:
        query["utm_term"] = term
    return urlunparse(parts._replace(query=urlencode(query)))


@dataclass
class Link:
    slug: str
    destination: str
    link_type: str
    campaign: str | None
    title: str | None
    clicks: int


class LinkRegistry:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS links (
                slug        TEXT PRIMARY KEY,
                destination TEXT NOT NULL,
                link_type   TEXT NOT NULL DEFAULT 'other',
                campaign    TEXT,
                title       TEXT,
                clicks      INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def add_link(
        self,
        slug: str,
        destination: str,
        link_type: str = "other",
        campaign: str | None = None,
        title: str | None = None,
        tag_utm: bool = True,
    ) -> Link:
        if link_type not in LINK_TYPES:
            raise ValueError(f"link_type must be one of {sorted(LINK_TYPES)}")
        if tag_utm:
            destination = build_utm_url(
                destination, campaign=campaign or slug, content=slug
            )
        self.conn.execute(
            "INSERT OR REPLACE INTO links (slug, destination, link_type, campaign, "
            "title, clicks, created_at) VALUES (?, ?, ?, ?, ?, "
            "COALESCE((SELECT clicks FROM links WHERE slug=?), 0), ?)",
            (
                slug,
                destination,
                link_type,
                campaign,
                title,
                slug,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self.conn.commit()
        return self.get(slug)

    def get(self, slug: str) -> Link:
        row = self.conn.execute(
            "SELECT * FROM links WHERE slug=?", (slug,)
        ).fetchone()
        if row is None:
            raise KeyError(slug)
        return Link(
            slug=row["slug"],
            destination=row["destination"],
            link_type=row["link_type"],
            campaign=row["campaign"],
            title=row["title"],
            clicks=row["clicks"],
        )

    def record_click(self, slug: str) -> None:
        self.conn.execute(
            "UPDATE links SET clicks = clicks + 1 WHERE slug=?", (slug,)
        )
        self.conn.commit()

    def list_links(self) -> list[Link]:
        rows = self.conn.execute(
            "SELECT * FROM links ORDER BY created_at"
        ).fetchall()
        return [
            Link(
                slug=r["slug"],
                destination=r["destination"],
                link_type=r["link_type"],
                campaign=r["campaign"],
                title=r["title"],
                clicks=r["clicks"],
            )
            for r in rows
        ]

    def export_bio(self) -> list[dict]:
        return [
            {"title": l.title or l.slug, "url": l.destination, "type": l.link_type}
            for l in self.list_links()
        ]

    def close(self) -> None:
        self.conn.close()


def render_link_in_bio(items: list[dict], page_title: str = "Links") -> str:
    """Render a dependency-free, static link-in-bio HTML page."""
    rows = "\n".join(
        f'    <a class="lnk" href="{html.escape(i["url"])}" '
        f'rel="nofollow sponsored noopener" target="_blank">'
        f'{html.escape(i["title"])}</a>'
        for i in items
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(page_title)}</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 480px; margin: 2rem auto;
         padding: 0 1rem; text-align: center; }}
  h1 {{ font-size: 1.25rem; }}
  .lnk {{ display: block; padding: 0.9rem; margin: 0.6rem 0; border-radius: 12px;
          border: 1px solid #ddd; text-decoration: none; color: #111; }}
  .lnk:hover {{ background: #f4f4f4; }}
</style>
</head>
<body>
  <h1>{html.escape(page_title)}</h1>
{rows}
  <p style="color:#999;font-size:.75rem;margin-top:2rem">Some links may be affiliate links.</p>
</body>
</html>
"""
