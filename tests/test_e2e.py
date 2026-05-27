from __future__ import annotations

import json
from pathlib import Path
import pytest

from app.config import get_settings
from app.data.repository import RestaurantRepository
from app.services.orchestrator import build_use_case
from app.services.llm_client import LLMClient
from app.models import UserPreferences


class MockLLMClient(LLMClient):
    def complete(self, prompt) -> str:
        # Standard structured mock response matching required schemas
        return json.dumps({
            "summary": "AI recommendation E2E mock summary",
            "recommendations": [
                {
                    "restaurant_id": "0",  # We will dynamically overwrite this inside the test to match a real candidate
                    "rank": 1,
                    "explanation": "Perfect E2E match explanation"
                }
            ]
        })


PARQUET = Path(__file__).resolve().parents[1] / "data" / "processed" / "restaurants.parquet"


@pytest.mark.skipif(not PARQUET.exists(), reason="Run ingest first to create parquet artifact")
def test_e2e_golden_path() -> None:
    # 1. Initialize settings and repository from actual data store
    settings = get_settings()
    repo = RestaurantRepository.from_parquet(settings.data_path)
    all_restaurants = repo.get_all()
    assert len(all_restaurants) > 0

    # 2. Extract a sample restaurant to build valid query preferences
    sample = all_restaurants[0]
    sample_cuisine = sample.cuisines[0] if sample.cuisines else "chinese"
    sample_location = sample.location
    sample_budget = sample.budget_band.value if sample.budget_band.value != "unknown" else "medium"

    # 3. Create mock LLM client returning the ID of the matched sample
    mock_llm = MockLLMClient()
    use_case = build_use_case(repo, mock_llm, max_candidates=20)

    # Override LLM mock return value to contain a valid ID from the repository
    def complete_override(prompt) -> str:
        return json.dumps({
            "summary": f"Selected restaurant fits {sample_location}",
            "recommendations": [
                {
                    "restaurant_id": str(sample.id),
                    "rank": 1,
                    "explanation": "Custom E2E match explanation"
                }
            ]
        })
    mock_llm.complete = complete_override

    # 4. Construct valid user preferences
    prefs = UserPreferences(
        location=sample_location,
        cuisine=sample_cuisine,
        budget=sample_budget,
        min_rating=0.0,  # Ensure we capture our sample candidate
        top_k=1,
        additional_preferences="quiet atmosphere"
    )

    # 5. Execute orchestrator
    result = use_case.execute(prefs)

    # 6. Assert result integrity
    assert result.summary == f"Selected restaurant fits {sample_location}"
    assert len(result.recommendations) == 1
    assert result.recommendations[0].rank == 1
    assert result.recommendations[0].restaurant.id == str(sample.id)
    assert result.recommendations[0].restaurant.name == sample.name
    assert result.recommendations[0].explanation == "Custom E2E match explanation"
    assert result.meta.candidates_considered > 0
    assert result.meta.fallback_used is False
