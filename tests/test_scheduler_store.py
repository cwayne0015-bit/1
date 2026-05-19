from datetime import datetime, timedelta, timezone

import pytest

from igkit.scheduler.store import ScheduleStore


@pytest.fixture()
def store(tmp_path):
    s = ScheduleStore(tmp_path / "t.db")
    yield s
    s.close()


def test_due_only_returns_past_pending(store):
    now = datetime(2026, 5, 19, 12, 0, tzinfo=timezone.utc)
    past = (now - timedelta(hours=1)).isoformat()
    future = (now + timedelta(hours=1)).isoformat()

    past_id = store.enqueue(past, "image", ["https://x/img.jpg"], "past")
    store.enqueue(future, "image", ["https://x/img2.jpg"], "future")

    due = store.due(now=now)
    assert [p.id for p in due] == [past_id]
    assert due[0].media_urls == ["https://x/img.jpg"]


def test_mark_published_and_failed(store):
    now = datetime.now(timezone.utc)
    pid = store.enqueue(now.isoformat(), "image", ["https://x/i.jpg"])
    store.mark_published(pid, "ig_123")
    assert store.list_all()[0].status == "published"
    assert store.list_all()[0].ig_media_id == "ig_123"

    pid2 = store.enqueue(now.isoformat(), "reel", ["https://x/v.mp4"])
    store.mark_failed(pid2, "boom")
    failed = [p for p in store.list_all() if p.id == pid2][0]
    assert failed.status == "failed" and failed.error == "boom"


def test_enqueue_rejects_bad_type(store):
    with pytest.raises(ValueError):
        store.enqueue(datetime.now(timezone.utc).isoformat(), "story", ["u"])
