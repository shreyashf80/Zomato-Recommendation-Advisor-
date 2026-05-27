from __future__ import annotations

from fastapi.testclient import TestClient
from app.main import app
from app.data.repository import RestaurantRepository
from app.services.orchestrator import RecommendRestaurantsUseCase
from app.services.filter_service import FilterService
from app.services.llm_client import LLMClient


class MockLLMClient(LLMClient):
    def complete(self, prompt: str) -> str:
        # Return a valid structured JSON recommendations response matching prompt specifications
        return (
            '{"summary": "Test recommendation summary", '
            '"recommendations": [{"restaurant_id": "r1", "rank": 1, "explanation": "Fits perfectly"}]}'
        )


def test_api_routes(repository: RestaurantRepository) -> None:
    # Set app state fixtures
    app.state.repository = repository
    app.state.use_case = RecommendRestaurantsUseCase(
        repository=repository,
        filter_service=FilterService(max_candidates=10),
        llm_client=MockLLMClient(),
    )

    client = TestClient(app)

    # 1. Verify health check endpoint
    health_res = client.get("/api/v1/health")
    assert health_res.status_code == 200
    assert health_res.json() == {"status": "ok"}

    # 2. Verify locations metadata endpoint
    loc_res = client.get("/api/v1/metadata/locations")
    assert loc_res.status_code == 200
    assert "Banashankari" in loc_res.json()
    assert "Koramangala" in loc_res.json()

    # 3. Verify cuisines metadata endpoint
    cuis_res = client.get("/api/v1/metadata/cuisines")
    assert cuis_res.status_code == 200
    assert "italian" in cuis_res.json()
    assert "chinese" in cuis_res.json()

    # 4. Verify recommendations POST endpoint
    payload = {
        "location": "Banashankari",
        "cuisine": "italian",
        "budget": "medium",
        "min_rating": 3.0,
        "top_k": 2,
        "additional_preferences": "rooftop seating",
    }
    rec_res = client.post("/api/v1/recommendations", json=payload)
    assert rec_res.status_code == 200
    data = rec_res.json()
    
    assert data["summary"] == "Test recommendation summary"
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["rank"] == 1
    assert data["recommendations"][0]["restaurant"]["id"] == "r1"
    assert data["recommendations"][0]["restaurant"]["name"] == "Alpha Bistro"
    assert data["meta"]["fallback_used"] is False
