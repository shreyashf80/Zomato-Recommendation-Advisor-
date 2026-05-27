from __future__ import annotations

import pytest

from app.data.repository import RestaurantRepository, StoreNotReadyError
from app.models import BudgetBand, FilterCriteria, Restaurant


def test_get_all(repository: RestaurantRepository) -> None:
    assert len(repository.get_all()) == 5


def test_get_by_ids(repository: RestaurantRepository) -> None:
    found = repository.get_by_ids(["r1", "missing", "r3"])
    assert [r.id for r in found] == ["r1", "r3"]


def test_filter_location(repository: RestaurantRepository) -> None:
    criteria = FilterCriteria(location="banashankari", budget="medium", cuisine="italian", min_rating=0.0)
    ids = {r.id for r in repository.filter(criteria)}
    assert ids == {"r1", "r4"}  # r5 has unknown budget_band


def test_filter_budget_excludes_unknown(repository: RestaurantRepository) -> None:
    criteria = FilterCriteria(location="banashankari", budget="medium", cuisine="italian", min_rating=0.0)
    ids = {r.id for r in repository.filter(criteria)}
    assert "r5" not in ids


def test_filter_cuisine(repository: RestaurantRepository) -> None:
    criteria = FilterCriteria(location="banashankari", budget="low", cuisine="chinese", min_rating=0.0)
    assert [r.id for r in repository.filter(criteria)] == ["r2"]


def test_filter_min_rating(repository: RestaurantRepository) -> None:
    criteria = FilterCriteria(location="banashankari", budget="medium", cuisine="italian", min_rating=4.0)
    ids = {r.id for r in repository.filter(criteria)}
    assert ids == {"r1"}


def test_filter_zero_matches(repository: RestaurantRepository) -> None:
    criteria = FilterCriteria(location="indiranagar", budget="low", cuisine="italian", min_rating=0.0)
    assert repository.filter(criteria) == []


def test_store_not_ready(tmp_path) -> None:
    with pytest.raises(StoreNotReadyError):
        RestaurantRepository.from_parquet(str(tmp_path / "missing.parquet"))
