from __future__ import annotations

from app.data.repository import RestaurantRepository
from app.models import BudgetBand, Restaurant
from app.models.user_preferences import UserPreferences
from app.services.filter_service import FilterService


def _prefs(**kwargs) -> UserPreferences:
    defaults = {
        "location": "Banashankari",
        "budget": "medium",
        "cuisine": "Italian",
        "min_rating": 0.0,
    }
    defaults.update(kwargs)
    return UserPreferences(**defaults)


def test_filter_service_returns_matches(repository: RestaurantRepository) -> None:
    svc = FilterService(max_candidates=30)
    result = svc.filter(_prefs(min_rating=4.0), repository)
    assert result.total_before_cap == 1
    assert len(result.candidates) == 1
    assert result.candidates[0].id == "r1"
    assert result.applied_filters["budget"] == "medium"


def test_filter_service_zero_matches(repository: RestaurantRepository) -> None:
    svc = FilterService()
    result = svc.filter(_prefs(location="Indiranagar"), repository)
    assert result.total_before_cap == 0
    assert result.candidates == []


def test_filter_service_candidate_cap() -> None:
    restaurants = [
        Restaurant(
            id=f"r{i}",
            name=f"Rest {i}",
            location="Banashankari",
            cuisines=["italian"],
            rating=float(i) / 10,
            budget_band=BudgetBand.medium,
            metadata={"votes": i},
        )
        for i in range(40)
    ]
    repo = RestaurantRepository(restaurants)
    svc = FilterService(max_candidates=10)
    result = svc.filter(_prefs(min_rating=0.0), repo)
    assert result.total_before_cap == 40
    assert len(result.candidates) == 10
    # Highest votes first, then rating
    assert result.candidates[0].metadata["votes"] == 39


def test_filter_service_sorts_by_votes_then_rating(repository: RestaurantRepository) -> None:
    svc = FilterService(max_candidates=30)
    result = svc.filter(_prefs(budget="low", cuisine="chinese", min_rating=0.0), repository)
    assert len(result.candidates) == 1
    assert result.candidates[0].id == "r2"
