"""AI content generation via the Anthropic API.

Design notes:
- The brand profile + instructions form a STABLE prefix and go in `system` with
  a `cache_control` breakpoint. The per-request topic is volatile and goes in
  the user turn, after the breakpoint, so the cached prefix stays byte-stable.
  (Opus has a ~4096-token minimum cacheable prefix; short brand prompts may not
  reach it and simply won't cache — harmless, no error.)
- Structured output is enforced with `messages.parse(output_format=Model)`.
- Adaptive thinking is the recommended mode on current models; `effort` tunes
  the cost/quality tradeoff for this high-volume use case.
"""

from __future__ import annotations

import anthropic

from igkit.config import Config
from igkit.content.models import BrandProfile, ContentPackage, IdeaList

_SYSTEM_INSTRUCTIONS = """\
You are a senior Instagram content strategist generating organic content for a \
single brand account. You write platform-native copy that respects Instagram's \
Terms of Use: no engagement-bait that violates policy, no fake claims, no \
follow-for-follow or giveaway-loophole tactics.

Rules:
- Match the brand voice exactly. Never use any banned word.
- Hashtags: a focused mix of niche, mid, and broad tags relevant to the post.
  Return them WITHOUT the leading '#'. No banned or shadowban-risk tags, no
  more than 20.
- Captions must be specific to the topic — no generic filler.
- Honour the emoji_usage setting.
- Calls to action should be drawn from the brand's cta_options when suitable.
- Output must conform exactly to the requested JSON schema.

The brand profile (authoritative) follows as JSON.
"""


class ContentGenerator:
    def __init__(
        self,
        brand: BrandProfile,
        config: Config | None = None,
        client: anthropic.Anthropic | None = None,
    ) -> None:
        self.brand = brand
        self.config = config or Config.from_env()
        if client is not None:
            self.client = client
        else:
            self.client = anthropic.Anthropic(api_key=self.config.require_anthropic())

    # The cacheable prefix: identical across every call for this brand.
    def _system(self) -> list[dict]:
        text = f"{_SYSTEM_INSTRUCTIONS}\n\nBRAND_PROFILE =\n{self.brand.stable_json()}"
        return [
            {
                "type": "text",
                "text": text,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    def _common_kwargs(self) -> dict:
        kwargs: dict = {
            "model": self.config.model,
            "max_tokens": 8000,
            "system": self._system(),
            "output_config": {"effort": self.config.effort},
        }
        if self.config.thinking:
            kwargs["thinking"] = {"type": "adaptive"}
        return kwargs

    def generate_captions(
        self, topic: str, n: int = 3, extra_guidance: str | None = None
    ) -> ContentPackage:
        prompt = (
            f"Generate {n} distinct caption variants for this post.\n"
            f"TOPIC: {topic}\n"
        )
        if extra_guidance:
            prompt += f"ADDITIONAL GUIDANCE: {extra_guidance}\n"
        prompt += "Vary the angle/structure across variants."

        response = self.client.messages.parse(
            messages=[{"role": "user", "content": prompt}],
            output_format=ContentPackage,
            **self._common_kwargs(),
        )
        return _parsed(response, ContentPackage)

    def generate_ideas(self, theme: str, n: int = 5) -> IdeaList:
        prompt = (
            f"Propose {n} post ideas for the content theme: {theme}.\n"
            "Each idea must be concretely actionable and on-brand. "
            "Spread across formats (Reel/Carousel/Single/Story) where it fits."
        )
        response = self.client.messages.parse(
            messages=[{"role": "user", "content": prompt}],
            output_format=IdeaList,
            **self._common_kwargs(),
        )
        return _parsed(response, IdeaList)


def _parsed(response, model):
    parsed = getattr(response, "parsed_output", None)
    if parsed is None:
        raise RuntimeError(
            f"Model did not return valid {model.__name__} "
            f"(stop_reason={getattr(response, 'stop_reason', '?')})."
        )
    return parsed
