"""Pydantic models: the brand profile (input) and structured generation outputs.

The output models double as the JSON schema for the Anthropic structured-output
feature via `client.messages.parse(output_format=...)`, so keep them flat and
avoid recursive types (unsupported by structured outputs).
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field


class BrandProfile(BaseModel):
    """Stable description of the account — used as the cacheable system prompt."""

    name: str
    niche: str
    audience: str
    voice: str = Field(description="Tone and personality, e.g. 'witty, warm, no jargon'")
    content_pillars: list[str] = Field(default_factory=list)
    cta_options: list[str] = Field(default_factory=list)
    banned_words: list[str] = Field(default_factory=list)
    emoji_usage: str = Field(
        default="sparing", description="one of: none | sparing | liberal"
    )
    languages: list[str] = Field(default_factory=lambda: ["en"])
    link_in_bio_url: str | None = None

    @classmethod
    def load(cls, path: str | Path) -> "BrandProfile":
        return cls.model_validate_json(Path(path).read_text(encoding="utf-8"))

    def stable_json(self) -> str:
        """Deterministic serialization so the cached prompt prefix is byte-stable."""
        return json.dumps(self.model_dump(), sort_keys=True, ensure_ascii=False, indent=2)


class CaptionVariant(BaseModel):
    caption: str = Field(description="Ready-to-post caption text, no hashtags inline")
    hashtags: list[str] = Field(description="Hashtags without the leading '#'")
    call_to_action: str
    rationale: str = Field(description="One sentence: why this angle should perform")


class ContentPackage(BaseModel):
    variants: list[CaptionVariant]
    alt_text: str = Field(description="Accessibility alt text describing the visual")


class PostIdea(BaseModel):
    hook: str = Field(description="Scroll-stopping first line")
    concept: str
    format: str = Field(description="Reel | Carousel | Single image | Story")
    suggested_caption: str
    hashtags: list[str]


class IdeaList(BaseModel):
    ideas: list[PostIdea]
