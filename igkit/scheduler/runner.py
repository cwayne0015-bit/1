"""Publish all due posts. Intended to run on a schedule (cron / CI job)."""

from __future__ import annotations

from datetime import datetime

from igkit.graph.client import GraphAPIError, InstagramGraphClient
from igkit.scheduler.store import ScheduledPost, ScheduleStore


def _publish_one(graph: InstagramGraphClient, post: ScheduledPost) -> str:
    if post.media_type == "image":
        return graph.publish_image(post.media_urls[0], post.caption)
    if post.media_type == "reel":
        return graph.publish_reel(post.media_urls[0], post.caption)
    if post.media_type == "carousel":
        return graph.publish_carousel(post.media_urls, post.caption)
    raise ValueError(f"Unknown media_type: {post.media_type}")


def run_due(
    store: ScheduleStore,
    graph: InstagramGraphClient,
    now: datetime | None = None,
) -> dict:
    """Publish every pending post whose time has arrived.

    Returns a summary dict: {"published": [...], "failed": [(id, error), ...]}.
    A failure on one post does not stop the rest.
    """
    published: list[int] = []
    failed: list[tuple[int, str]] = []

    for post in store.due(now):
        try:
            media_id = _publish_one(graph, post)
            store.mark_published(post.id, media_id)
            published.append(post.id)
        except (GraphAPIError, ValueError) as exc:
            store.mark_failed(post.id, str(exc))
            failed.append((post.id, str(exc)))

    return {"published": published, "failed": failed}
