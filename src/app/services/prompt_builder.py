from __future__ import annotations

import json
from dataclasses import dataclass

from ..models import Restaurant, UserPreferences

MAX_ADDITIONAL_PREFS_LEN = 500


@dataclass(frozen=True)
class Prompt:
    system: str
    user: str


class PromptBuilder:
    def build(self, preferences: UserPreferences, candidates: list[Restaurant]) -> Prompt:
        allowed_ids = [r.id for r in candidates]
        candidate_payload = [
            {
                "restaurant_id": r.id,
                "name": r.name,
                "location": r.location,
                "cuisines": r.cuisines,
                "rating": r.rating,
                "estimated_cost": r.estimated_cost,
                "budget_band": r.budget_band.value,
            }
            for r in candidates
        ]

        extras = preferences.additional_preferences
        if extras and len(extras) > MAX_ADDITIONAL_PREFS_LEN:
            extras = extras[:MAX_ADDITIONAL_PREFS_LEN] + "..."

        system = (
            "You are a restaurant recommendation advisor. "
            "Recommend ONLY from the candidate list provided. "
            "Never invent restaurants or use IDs not in the allowed list. "
            "Respond with valid JSON only, matching the required schema."
        )

        user = json.dumps(
            {
                "task": f"Rank the top {preferences.top_k} restaurants for this user.",
                "user_preferences": {
                    "location": preferences.location,
                    "budget": preferences.budget,
                    "cuisine": preferences.cuisine,
                    "min_rating": preferences.min_rating,
                    "additional_preferences": extras,
                },
                "allowed_restaurant_ids": allowed_ids,
                "candidates": candidate_payload,
                "output_schema": {
                    "summary": "Brief overview of the selection.",
                    "recommendations": [
                        {
                            "restaurant_id": "id from allowed_restaurant_ids",
                            "rank": 1,
                            "explanation": "Why this fits the user preferences.",
                        }
                    ],
                },
            },
            indent=2,
            ensure_ascii=False,
        )

        return Prompt(system=system, user=user)
