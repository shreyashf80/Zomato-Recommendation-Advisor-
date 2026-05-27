from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..data.repository import RestaurantRepository
from ..models import FilterCriteria, Restaurant, UserPreferences


@dataclass(frozen=True)
class FilterResult:
    candidates: list[Restaurant]
    total_before_cap: int
    applied_filters: dict[str, Any]


class FilterService:
    def __init__(self, max_candidates: int = 30) -> None:
        self.max_candidates = max_candidates

    def filter(
        self,
        preferences: UserPreferences,
        repository: RestaurantRepository,
    ) -> FilterResult:
        criteria = FilterCriteria.from_preferences(preferences)
        matched = repository.filter(criteria)

        sorted_matches = sorted(
            matched,
            key=lambda r: (_votes(r), r.rating),
            reverse=True,
        )

        total_before_cap = len(sorted_matches)
        capped = sorted_matches[: self.max_candidates]

        return FilterResult(
            candidates=capped,
            total_before_cap=total_before_cap,
            applied_filters={
                "location": criteria.location,
                "budget": criteria.budget,
                "cuisine": criteria.cuisine,
                "min_rating": criteria.min_rating,
                "max_candidates": self.max_candidates,
            },
        )


def _votes(restaurant: Restaurant) -> int:
    raw = restaurant.metadata.get("votes")
    if raw is None:
        return 0
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 0
