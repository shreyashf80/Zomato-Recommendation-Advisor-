from __future__ import annotations

from pathlib import Path

import pytest

from app.config import get_settings
from app.data.repository import RestaurantRepository, StoreNotReadyError
from app.models import FilterCriteria


PARQUET = Path(__file__).resolve().parents[1] / "data" / "processed" / "restaurants.parquet"


@pytest.mark.skipif(not PARQUET.exists(), reason="Run ingest first to create parquet artifact")
def test_load_parquet_and_filter() -> None:
    settings = get_settings()
    repo = RestaurantRepository.from_parquet(settings.data_path)
    all_rows = repo.get_all()
    assert len(all_rows) > 0

    sample_location = all_rows[0].location
    criteria = FilterCriteria(
        location=sample_location.lower(),
        budget="medium",
        cuisine="italian",
        min_rating=0.0,
    )
    matches = repo.filter(criteria)
    assert isinstance(matches, list)
