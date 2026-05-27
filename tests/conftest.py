from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.data.repository import RestaurantRepository  # noqa: E402
from app.models import BudgetBand, Restaurant  # noqa: E402


@pytest.fixture
def sample_restaurants() -> list[Restaurant]:
    return [
        Restaurant(
            id="r1",
            name="Alpha Bistro",
            location="Banashankari",
            cuisines=["italian", "continental"],
            rating=4.5,
            estimated_cost=800.0,
            budget_band=BudgetBand.medium,
            metadata={"votes": 500},
        ),
        Restaurant(
            id="r2",
            name="Beta Diner",
            location="Banashankari",
            cuisines=["chinese", "thai"],
            rating=4.0,
            estimated_cost=400.0,
            budget_band=BudgetBand.low,
            metadata={"votes": 900},
        ),
        Restaurant(
            id="r3",
            name="Gamma Grill",
            location="Koramangala",
            cuisines=["italian"],
            rating=3.8,
            estimated_cost=2000.0,
            budget_band=BudgetBand.high,
            metadata={"votes": 100},
        ),
        Restaurant(
            id="r4",
            name="Delta Cafe",
            location="Banashankari",
            cuisines=["italian"],
            rating=2.5,
            estimated_cost=600.0,
            budget_band=BudgetBand.medium,
            metadata={"votes": 50},
        ),
        Restaurant(
            id="r5",
            name="Epsilon Eats",
            location="Banashankari",
            cuisines=["italian"],
            rating=4.2,
            estimated_cost=300.0,
            budget_band=BudgetBand.unknown,
            metadata={"votes": 10},
        ),
    ]


@pytest.fixture
def repository(sample_restaurants: list[Restaurant]) -> RestaurantRepository:
    return RestaurantRepository(sample_restaurants)
