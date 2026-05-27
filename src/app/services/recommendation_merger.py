from __future__ import annotations

from typing import Optional

from ..models import Recommendation, Restaurant
from .response_parser import ParsedLLMResponse


FALLBACK_EXPLANATION = (
    "Recommended based on rating and your filters (fallback ranking; LLM unavailable)."
)


class RecommendationMerger:
    def merge(
        self,
        parsed: ParsedLLMResponse,
        candidates: list[Restaurant],
        *,
        top_k: int,
    ) -> list[Recommendation]:
        by_id = {r.id: r for r in candidates}
        results: list[Recommendation] = []

        for item in parsed.recommendations:
            restaurant = by_id.get(item.restaurant_id)
            if restaurant is None:
                continue
            results.append(
                Recommendation(
                    restaurant=restaurant,
                    rank=item.rank,
                    explanation=item.explanation,
                )
            )
            if len(results) >= top_k:
                break

        if len(results) < top_k:
            results = self._fill_from_candidates(
                results,
                candidates,
                top_k=top_k,
                explanation_prefix=None,
            )

        results.sort(key=lambda r: r.rank)
        # Normalize ranks to 1..N
        normalized: list[Recommendation] = []
        for idx, rec in enumerate(results[:top_k], start=1):
            normalized.append(
                Recommendation(
                    restaurant=rec.restaurant,
                    rank=idx,
                    explanation=rec.explanation,
                )
            )
        return normalized

    def fallback(
        self,
        candidates: list[Restaurant],
        *,
        top_k: int,
    ) -> list[Recommendation]:
        sorted_candidates = sorted(
            candidates,
            key=lambda r: (r.rating, _votes(r)),
            reverse=True,
        )
        return [
            Recommendation(
                restaurant=r,
                rank=i,
                explanation=FALLBACK_EXPLANATION,
            )
            for i, r in enumerate(sorted_candidates[:top_k], start=1)
        ]


    def _fill_from_candidates(
        self,
        existing: list[Recommendation],
        candidates: list[Restaurant],
        *,
        top_k: int,
        explanation_prefix: Optional[str],
    ) -> list[Recommendation]:
        used_ids = {r.restaurant.id for r in existing}
        remaining = [c for c in candidates if c.id not in used_ids]
        remaining.sort(key=lambda r: (r.rating, _votes(r)), reverse=True)

        results = list(existing)
        next_rank = max((r.rank for r in results), default=0) + 1
        for r in remaining:
            if len(results) >= top_k:
                break
            expl = FALLBACK_EXPLANATION
            if explanation_prefix:
                expl = explanation_prefix
            results.append(
                Recommendation(
                    restaurant=r,
                    rank=next_rank,
                    explanation=expl,
                )
            )
            next_rank += 1
        return results


def _votes(restaurant: Restaurant) -> int:
    raw = restaurant.metadata.get("votes")
    if raw is None:
        return 0
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 0
