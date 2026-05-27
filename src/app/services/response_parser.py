from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class ParsedRecommendation:
    restaurant_id: str
    rank: int
    explanation: str


@dataclass(frozen=True)
class ParsedLLMResponse:
    summary: Optional[str]
    recommendations: list[ParsedRecommendation]


class ResponseParser:
    def parse(self, raw: str, *, allowed_ids: set[str]) -> ParsedLLMResponse:
        data = self._load_json(raw)
        summary = data.get("summary")
        if summary is not None:
            summary = str(summary).strip() or None

        recs_raw = data.get("recommendations") or []
        if not isinstance(recs_raw, list):
            raise ValueError("recommendations must be a list")

        parsed: list[ParsedRecommendation] = []
        seen_ids: set[str] = set()
        for item in recs_raw:
            if not isinstance(item, dict):
                continue
            rid = str(item.get("restaurant_id", "")).strip()
            if not rid or rid not in allowed_ids or rid in seen_ids:
                continue
            try:
                rank = int(item.get("rank", 0))
            except (TypeError, ValueError):
                continue
            if rank < 1:
                continue
            explanation = str(item.get("explanation", "")).strip()
            if not explanation:
                explanation = "Matches your preferences based on rating and filters."
            parsed.append(
                ParsedRecommendation(
                    restaurant_id=rid,
                    rank=rank,
                    explanation=explanation,
                )
            )
            seen_ids.add(rid)

        if not parsed:
            raise ValueError("no valid recommendations in LLM response")

        parsed.sort(key=lambda r: r.rank)
        return ParsedLLMResponse(summary=summary, recommendations=parsed)

    def _load_json(self, raw: str) -> dict[str, Any]:
        text = raw.strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            extracted = _extract_json_block(text)
            if not extracted:
                raise ValueError("response is not valid JSON") from None
            data = json.loads(extracted)

        if not isinstance(data, dict):
            raise ValueError("response JSON must be an object")
        return data


def _extract_json_block(text: str) -> Optional[str]:
    match = re.search(r"\{[\s\S]*\}", text)
    return match.group(0) if match else None
