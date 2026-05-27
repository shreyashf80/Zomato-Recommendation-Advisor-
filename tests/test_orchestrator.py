from __future__ import annotations

import json

import pytest

from app.data.repository import RestaurantRepository
from app.models import BudgetBand, Restaurant, UserPreferences
from app.services.filter_service import FilterService
from app.services.llm_client import LLMClientError, MockLLMClient
from app.services.orchestrator import RecommendRestaurantsUseCase


def _prefs(**kwargs) -> UserPreferences:
    defaults = {
        "location": "Banashankari",
        "budget": "medium",
        "cuisine": "Italian",
        "min_rating": 4.0,
        "top_k": 2,
    }
    defaults.update(kwargs)
    return UserPreferences(**defaults)


def _mock_llm_response(*, summary: str, items: list[dict]) -> str:
    return json.dumps({"summary": summary, "recommendations": items})


@pytest.fixture
def repository(sample_restaurants: list[Restaurant]) -> RestaurantRepository:
    return RestaurantRepository(sample_restaurants)


def test_orchestrator_empty_candidates(repository: RestaurantRepository) -> None:
    use_case = RecommendRestaurantsUseCase(
        repository=repository,
        filter_service=FilterService(max_candidates=30),
        llm_client=MockLLMClient("{}"),
    )
    result = use_case.execute(_prefs(location="Indiranagar"))
    assert result.recommendations == []
    assert result.meta.candidates_considered == 0
    assert result.meta.fallback_used is False
    assert "No restaurants matched" in (result.summary or "")


def test_orchestrator_with_mock_llm(repository: RestaurantRepository) -> None:
    llm_json = _mock_llm_response(
        summary="Two great Italian spots in Banashankari.",
        items=[
            {
                "restaurant_id": "r1",
                "rank": 1,
                "explanation": "Top-rated Italian with continental options.",
            },
            {
                "restaurant_id": "r4",
                "rank": 2,
                "explanation": "Solid Italian choice within budget.",
            },
        ],
    )
    mock = MockLLMClient(llm_json)
    use_case = RecommendRestaurantsUseCase(
        repository=repository,
        filter_service=FilterService(max_candidates=30),
        llm_client=mock,
    )

    result = use_case.execute(_prefs(min_rating=2.0))

    assert result.summary == "Two great Italian spots in Banashankari."
    assert len(result.recommendations) == 2
    assert result.recommendations[0].rank == 1
    assert result.recommendations[0].restaurant.id == "r1"
    assert result.recommendations[0].explanation.startswith("Top-rated")
    assert result.recommendations[1].restaurant.id == "r4"
    assert result.meta.candidates_considered == 2
    assert result.meta.fallback_used is False
    assert "location" in result.meta.filters_applied
    assert mock.last_prompt is not None


def test_orchestrator_fallback_on_invalid_llm_response(
    repository: RestaurantRepository,
) -> None:
    mock = MockLLMClient("not valid json at all")
    use_case = RecommendRestaurantsUseCase(
        repository=repository,
        filter_service=FilterService(max_candidates=30),
        llm_client=mock,
    )
    result = use_case.execute(_prefs(min_rating=2.0, top_k=1))

    assert len(result.recommendations) == 1
    assert result.meta.fallback_used is True
    assert result.recommendations[0].restaurant.id == "r1"  # highest rating among matches


class FailingLLMClient:
    def complete(self, prompt):  # noqa: ANN001
        raise LLMClientError("upstream failure")


def test_orchestrator_fallback_on_llm_error(repository: RestaurantRepository) -> None:
    use_case = RecommendRestaurantsUseCase(
        repository=repository,
        filter_service=FilterService(max_candidates=30),
        llm_client=FailingLLMClient(),
    )
    result = use_case.execute(_prefs(min_rating=2.0, top_k=2))

    assert len(result.recommendations) == 2
    assert result.meta.fallback_used is True
    assert all("fallback" in r.explanation.lower() for r in result.recommendations)
