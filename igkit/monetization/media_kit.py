"""Generate a brand-deal media kit (Markdown) from live Graph API insights.

Covers the 'brand deals / sponsorships' path: pulls real account stats so
outreach numbers are accurate rather than guessed.
"""

from __future__ import annotations

from datetime import datetime, timezone

from igkit.graph.client import GraphAPIError, InstagramGraphClient


def _safe_account(graph: InstagramGraphClient) -> dict:
    try:
        return graph.get_account(
            "username,name,followers_count,media_count,biography"
        )
    except GraphAPIError:
        return {}


def _safe_reach(graph: InstagramGraphClient) -> int | None:
    try:
        data = graph.get_account_insights(
            ["reach"], period="day", metric_type="total_value"
        )
        values = data.get("data", [])
        if values and "total_value" in values[0]:
            return values[0]["total_value"].get("value")
    except GraphAPIError:
        return None
    return None


def build_media_kit(
    graph: InstagramGraphClient,
    *,
    contact_email: str,
    rate_card: dict[str, str] | None = None,
    highlights: list[str] | None = None,
) -> str:
    """Return a Markdown media kit. `rate_card` maps deliverable -> price."""
    account = _safe_account(graph)
    reach = _safe_reach(graph)
    followers = account.get("followers_count")
    media_count = account.get("media_count")
    username = account.get("username", "your_account")

    lines: list[str] = []
    lines.append(f"# Media Kit — @{username}")
    if account.get("name"):
        lines.append(f"**{account['name']}**")
    lines.append("")
    if account.get("biography"):
        lines.append(f"> {account['biography']}")
        lines.append("")

    lines.append("## Audience & Reach")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Followers | {followers if followers is not None else 'n/a'} |")
    lines.append(f"| Posts | {media_count if media_count is not None else 'n/a'} |")
    lines.append(f"| Reach (last 24h) | {reach if reach is not None else 'n/a'} |")
    lines.append("")

    if highlights:
        lines.append("## Highlights")
        lines.append("")
        for h in highlights:
            lines.append(f"- {h}")
        lines.append("")

    lines.append("## Collaboration Options")
    lines.append("")
    if rate_card:
        lines.append("| Deliverable | Rate |")
        lines.append("| --- | --- |")
        for deliverable, price in rate_card.items():
            lines.append(f"| {deliverable} | {price} |")
    else:
        lines.append("_Rates available on request._")
    lines.append("")

    lines.append("## Contact")
    lines.append("")
    lines.append(f"For partnerships: **{contact_email}**")
    lines.append("")
    lines.append(
        f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d')}. "
        "Figures sourced directly from the Instagram Graph API._"
    )
    return "\n".join(lines)
