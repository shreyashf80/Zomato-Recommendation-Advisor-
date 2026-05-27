from __future__ import annotations

import json

from app.models import BudgetBand, Restaurant
from app.models.user_preferences import UserPreferences
from app.services.prompt_builder import PromptBuilder


def test_prompt_builder_includes_allowed_ids_and_schema() -> None:
    prefs = UserPreferences(
        location="Banashankari",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        top_k=3,
    )
    candidates = [
        Restaurant(
            id="abc123",
            name="Test Place",
            location="Banashankari",
            cuisines=["italian"],
            rating=4.5,
            budget_band=BudgetBand.medium,
        )
    ]
    prompt = PromptBuilder().build(prefs, candidates)

    assert "abc123" in prompt.user
    assert "allowed_restaurant_ids" in prompt.user
    assert "Never invent restaurants" in prompt.system

    payload = json.loads(prompt.user)
    assert payload["allowed_restaurant_ids"] == ["abc123"]
    assert payload["task"] == "Rank the top 3 restaurants for this user."
