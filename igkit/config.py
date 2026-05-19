"""Environment-driven configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:  # optional convenience — load a local .env if python-dotenv is installed
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional
    pass

_VALID_EFFORT = {"low", "medium", "high", "max"}


@dataclass(frozen=True)
class Config:
    anthropic_api_key: str | None
    model: str
    effort: str
    thinking: bool
    ig_access_token: str | None
    ig_user_id: str | None
    ig_graph_version: str
    db_path: Path

    @classmethod
    def from_env(cls) -> "Config":
        effort = os.environ.get("CONTENT_EFFORT", "medium").strip().lower()
        if effort not in _VALID_EFFORT:
            effort = "medium"
        thinking = os.environ.get("CONTENT_THINKING", "on").strip().lower() != "off"
        return cls(
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
            model=os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-7").strip(),
            effort=effort,
            thinking=thinking,
            ig_access_token=os.environ.get("IG_ACCESS_TOKEN"),
            ig_user_id=os.environ.get("IG_USER_ID"),
            ig_graph_version=os.environ.get("IG_GRAPH_VERSION", "v21.0").strip(),
            db_path=Path(os.environ.get("IGKIT_DB", "data/igkit.db")),
        )

    def require_anthropic(self) -> str:
        if not self.anthropic_api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and fill it in."
            )
        return self.anthropic_api_key

    def require_graph(self) -> tuple[str, str]:
        if not self.ig_access_token or not self.ig_user_id:
            raise RuntimeError(
                "IG_ACCESS_TOKEN and IG_USER_ID must be set for Graph API calls. "
                "See the README for the Meta app setup walkthrough."
            )
        return self.ig_access_token, self.ig_user_id
