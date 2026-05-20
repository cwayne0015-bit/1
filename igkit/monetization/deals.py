"""A minimal sponsorship-deal pipeline (CRM) — track brand deals from outreach
to paid. Covers the 'brand deals / sponsorships' path.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

STAGES = ["lead", "negotiating", "agreed", "delivered", "paid", "lost"]


@dataclass
class SponsorshipDeal:
    id: int
    brand: str
    contact: str | None
    stage: str
    fee: float | None
    deliverables: str | None
    due_date: str | None
    notes: str | None


class DealStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS deals (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                brand        TEXT NOT NULL,
                contact      TEXT,
                stage        TEXT NOT NULL DEFAULT 'lead',
                fee          REAL,
                deliverables TEXT,
                due_date     TEXT,
                notes        TEXT,
                created_at   TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def _row(self, r: sqlite3.Row) -> SponsorshipDeal:
        return SponsorshipDeal(
            id=r["id"],
            brand=r["brand"],
            contact=r["contact"],
            stage=r["stage"],
            fee=r["fee"],
            deliverables=r["deliverables"],
            due_date=r["due_date"],
            notes=r["notes"],
        )

    def add(
        self,
        brand: str,
        contact: str | None = None,
        fee: float | None = None,
        deliverables: str | None = None,
        due_date: str | None = None,
        notes: str | None = None,
    ) -> int:
        cur = self.conn.execute(
            "INSERT INTO deals (brand, contact, stage, fee, deliverables, "
            "due_date, notes, created_at) VALUES (?, ?, 'lead', ?, ?, ?, ?, ?)",
            (
                brand,
                contact,
                fee,
                deliverables,
                due_date,
                notes,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def set_stage(self, deal_id: int, stage: str) -> None:
        if stage not in STAGES:
            raise ValueError(f"stage must be one of {STAGES}")
        self.conn.execute(
            "UPDATE deals SET stage=? WHERE id=?", (stage, deal_id)
        )
        self.conn.commit()

    def list_all(self) -> list[SponsorshipDeal]:
        rows = self.conn.execute(
            "SELECT * FROM deals ORDER BY "
            "CASE stage WHEN 'lead' THEN 0 WHEN 'negotiating' THEN 1 "
            "WHEN 'agreed' THEN 2 WHEN 'delivered' THEN 3 WHEN 'paid' THEN 4 "
            "ELSE 5 END, created_at"
        ).fetchall()
        return [self._row(r) for r in rows]

    def pipeline_value(self) -> dict[str, float]:
        """Sum of fees by stage — quick revenue forecast."""
        totals: dict[str, float] = {s: 0.0 for s in STAGES}
        for d in self.list_all():
            if d.fee:
                totals[d.stage] = totals.get(d.stage, 0.0) + d.fee
        return totals

    def close(self) -> None:
        self.conn.close()
