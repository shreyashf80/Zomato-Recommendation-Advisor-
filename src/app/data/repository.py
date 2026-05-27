from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pandas as pd

from ..models import BudgetBand, FilterCriteria, Restaurant


class StoreNotReadyError(Exception):
    """Raised when the processed restaurant artifact is missing or invalid."""


class RestaurantRepository:
    def __init__(self, restaurants: list[Restaurant]) -> None:
        self._restaurants = restaurants
        self._by_id = {r.id: r for r in restaurants}

    @classmethod
    def from_parquet(cls, path: str) -> "RestaurantRepository":
        p = Path(path).expanduser().resolve()
        if not p.exists():
            raise StoreNotReadyError(
                f"Processed data not found at {p}. Run `python scripts/ingest.py` first."
            )
        try:
            df = pd.read_parquet(p)
        except Exception as exc:
            raise StoreNotReadyError(f"Failed to read restaurant store at {p}: {exc}") from exc

        required = {"id", "name", "location", "cuisines", "rating", "budget_band"}
        missing = required - set(df.columns)
        if missing:
            raise StoreNotReadyError(f"Invalid schema at {p}; missing columns: {sorted(missing)}")

        restaurants = [_row_to_restaurant(row) for _, row in df.iterrows()]
        return cls(restaurants)

    def get_all(self) -> list[Restaurant]:
        return list(self._restaurants)

    def get_by_ids(self, ids: list[str]) -> list[Restaurant]:
        return [self._by_id[i] for i in ids if i in self._by_id]

    def filter(self, criteria: FilterCriteria) -> list[Restaurant]:
        loc = criteria.location_normalized
        cuisine = criteria.cuisine_normalized
        budget = criteria.budget

        results: list[Restaurant] = []
        for r in self._restaurants:
            if loc not in r.location.lower():
                continue
            if r.budget_band.value != budget:
                continue
            if not any(cuisine in c or c in cuisine for c in r.cuisines):
                continue
            if r.rating < criteria.min_rating:
                continue
            results.append(r)
        return results


def _row_to_restaurant(row: pd.Series) -> Restaurant:
    cuisines = row.get("cuisines")
    if cuisines is None or (isinstance(cuisines, float) and pd.isna(cuisines)):
        cuisines_list: list[str] = []
    elif isinstance(cuisines, list):
        cuisines_list = [str(c).strip().lower() for c in cuisines if str(c).strip()]
    else:
        cuisines_list = [str(cuisines).strip().lower()]

    cost = row.get("estimated_cost")
    estimated_cost: Optional[float] = None
    if cost is not None and not (isinstance(cost, float) and pd.isna(cost)):
        estimated_cost = float(cost)

    band_raw = row.get("budget_band", BudgetBand.unknown.value)
    try:
        budget_band = BudgetBand(str(band_raw))
    except ValueError:
        budget_band = BudgetBand.unknown

    metadata: dict = {}
    if "metadata_json" in row.index and row.get("metadata_json") not in (None, ""):
        try:
            metadata = json.loads(row["metadata_json"])
        except (json.JSONDecodeError, TypeError):
            metadata = {}
    elif "metadata" in row.index and isinstance(row.get("metadata"), dict):
        metadata = row["metadata"]

    return Restaurant(
        id=str(row["id"]),
        name=str(row["name"]),
        location=str(row["location"]),
        cuisines=cuisines_list,
        rating=float(row.get("rating", 0.0) or 0.0),
        estimated_cost=estimated_cost,
        budget_band=budget_band,
        metadata=metadata,
    )
