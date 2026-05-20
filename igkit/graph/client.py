"""Thin client over the official Instagram Graph API.

Publishing is the standard two-step flow: create a media container, then
publish it. Video/Reels containers are processed asynchronously, so we poll
the container's `status_code` until it is FINISHED before publishing.

Docs: https://developers.facebook.com/docs/instagram-api/guides/content-publishing
This uses only officially supported endpoints — it is not a bot.
"""

from __future__ import annotations

import time

import requests

_BASE = "https://graph.facebook.com"


class GraphAPIError(RuntimeError):
    pass


class InstagramGraphClient:
    def __init__(
        self,
        access_token: str,
        ig_user_id: str,
        version: str = "v21.0",
        session: requests.Session | None = None,
        timeout: int = 30,
    ) -> None:
        self.access_token = access_token
        self.ig_user_id = ig_user_id
        self.version = version
        self.timeout = timeout
        self.session = session or requests.Session()

    # --- low-level helpers ---------------------------------------------------
    def _url(self, path: str) -> str:
        return f"{_BASE}/{self.version}/{path.lstrip('/')}"

    def _request(self, method: str, path: str, params: dict) -> dict:
        params = {**params, "access_token": self.access_token}
        resp = self.session.request(
            method, self._url(path), params=params, timeout=self.timeout
        )
        try:
            data = resp.json()
        except ValueError:
            raise GraphAPIError(f"Non-JSON response ({resp.status_code}): {resp.text[:200]}")
        if resp.status_code >= 400 or "error" in data:
            err = data.get("error", {})
            raise GraphAPIError(
                f"Graph API error {resp.status_code}: "
                f"{err.get('message', data)} (code={err.get('code')})"
            )
        return data

    # --- account & insights --------------------------------------------------
    def get_account(
        self, fields: str = "username,followers_count,media_count,biography"
    ) -> dict:
        return self._request("GET", self.ig_user_id, {"fields": fields})

    def get_account_insights(
        self, metrics: list[str], period: str = "day", metric_type: str | None = None
    ) -> dict:
        params: dict = {"metric": ",".join(metrics), "period": period}
        if metric_type:
            params["metric_type"] = metric_type
        return self._request("GET", f"{self.ig_user_id}/insights", params)

    def get_media_insights(self, media_id: str, metrics: list[str]) -> dict:
        return self._request(
            "GET", f"{media_id}/insights", {"metric": ",".join(metrics)}
        )

    def list_recent_media(self, limit: int = 25) -> dict:
        return self._request(
            "GET",
            f"{self.ig_user_id}/media",
            {"fields": "id,caption,media_type,timestamp,permalink", "limit": limit},
        )

    # --- publishing ----------------------------------------------------------
    def _create_container(self, params: dict) -> str:
        data = self._request("POST", f"{self.ig_user_id}/media", params)
        return data["id"]

    def _wait_for_container(
        self, creation_id: str, attempts: int = 30, delay: float = 5.0
    ) -> None:
        for _ in range(attempts):
            data = self._request(
                "GET", creation_id, {"fields": "status_code,status"}
            )
            status = data.get("status_code")
            if status == "FINISHED":
                return
            if status == "ERROR":
                raise GraphAPIError(f"Container processing failed: {data.get('status')}")
            time.sleep(delay)
        raise GraphAPIError("Timed out waiting for media container to finish processing.")

    def _publish(self, creation_id: str) -> str:
        data = self._request(
            "POST", f"{self.ig_user_id}/media_publish", {"creation_id": creation_id}
        )
        return data["id"]

    def publish_image(self, image_url: str, caption: str = "") -> str:
        cid = self._create_container({"image_url": image_url, "caption": caption})
        return self._publish(cid)

    def publish_reel(self, video_url: str, caption: str = "") -> str:
        cid = self._create_container(
            {"media_type": "REELS", "video_url": video_url, "caption": caption}
        )
        self._wait_for_container(cid)
        return self._publish(cid)

    def publish_carousel(self, image_urls: list[str], caption: str = "") -> str:
        if not 2 <= len(image_urls) <= 10:
            raise ValueError("A carousel needs between 2 and 10 items.")
        children = [
            self._create_container({"image_url": u, "is_carousel_item": "true"})
            for u in image_urls
        ]
        cid = self._create_container(
            {
                "media_type": "CAROUSEL",
                "children": ",".join(children),
                "caption": caption,
            }
        )
        return self._publish(cid)
