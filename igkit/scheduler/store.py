"""SQLite-backed post queue. No daemon — `run_due` is meant to be driven by
cron / a scheduled CI job, which is the ToS-compliant way to schedule posts.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

VALID_TYPES = {"image", "reel", "carousel"}


@dataclass
class ScheduledPost:
    id: int
    scheduled_at: str
    media_type: str
    media_urls: list[str]
    caption: str
    status: str
    ig_media_id: str | None
    error: str | None


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ScheduleStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                scheduled_at TEXT NOT NULL,
                media_type   TEXT NOT NULL,
                media_urls   TEXT NOT NULL,
                caption      TEXT NOT NULL DEFAULT '',
                status       TEXT NOT NULL DEFAULT 'pending',
                ig_media_id  TEXT,
                error        TEXT,
                created_at   TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def enqueue(
        self,
        scheduled_at: str,
        media_type: str,
        media_urls: list[str],
        caption: str = "",
    ) -> int:
        if media_type not in VALID_TYPES:
            raise ValueError(f"media_type must be one of {sorted(VALID_TYPES)}")
        # Normalize/validate the timestamp up front so failures surface at enqueue.
        datetime.fromisoformat(scheduled_at)
        cur = self.conn.execute(
            "INSERT INTO posts (scheduled_at, media_type, media_urls, caption, "
            "status, created_at) VALUES (?, ?, ?, ?, 'pending', ?)",
            (
                scheduled_at,
                media_type,
                json.dumps(media_urls),
                caption,
                _utcnow_iso(),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def _row(self, row: sqlite3.Row) -> ScheduledPost:
        return ScheduledPost(
            id=row["id"],
            scheduled_at=row["scheduled_at"],
            media_type=row["media_type"],
            media_urls=json.loads(row["media_urls"]),
            caption=row["caption"],
            status=row["status"],
            ig_media_id=row["ig_media_id"],
            error=row["error"],
        )

    def due(self, now: datetime | None = None) -> list[ScheduledPost]:
        now = now or datetime.now(timezone.utc)
        rows = self.conn.execute(
            "SELECT * FROM posts WHERE status = 'pending' "
            "AND scheduled_at <= ? ORDER BY scheduled_at",
            (now.isoformat(),),
        ).fetchall()
        return [self._row(r) for r in rows]

    def list_all(self) -> list[ScheduledPost]:
        rows = self.conn.execute(
            "SELECT * FROM posts ORDER BY scheduled_at"
        ).fetchall()
        return [self._row(r) for r in rows]

    def mark_published(self, post_id: int, ig_media_id: str) -> None:
        self.conn.execute(
            "UPDATE posts SET status='published', ig_media_id=?, error=NULL WHERE id=?",
            (ig_media_id, post_id),
        )
        self.conn.commit()

    def mark_failed(self, post_id: int, error: str) -> None:
        self.conn.execute(
            "UPDATE posts SET status='failed', error=? WHERE id=?", (error, post_id)
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
