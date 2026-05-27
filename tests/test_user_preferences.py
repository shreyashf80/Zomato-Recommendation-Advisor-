from __future__ import annotations

import pytest

from app.models.user_preferences import UserPreferences


def test_user_preferences_validation() -> None:
    p = UserPreferences(
        location="  Bangalore ",
        budget="medium",
        cuisine=" Italian ",
        min_rating=3.5,
    )
    assert p.location_normalized == "bangalore"
    assert p.cuisine_normalized == "italian"


def test_user_preferences_rejects_empty_location() -> None:
    with pytest.raises(ValueError):
        UserPreferences(location="  ", budget="low", cuisine="italian", min_rating=3.0)


def test_user_preferences_rejects_invalid_rating() -> None:
    with pytest.raises(ValueError):
        UserPreferences(location="Bangalore", budget="low", cuisine="italian", min_rating=6.0)


def test_user_preferences_rejects_long_additional_preferences() -> None:
    long_pref = "a" * 501
    with pytest.raises(ValueError):
        UserPreferences(
            location="Bangalore",
            budget="low",
            cuisine="italian",
            min_rating=4.0,
            additional_preferences=long_pref,
        )

