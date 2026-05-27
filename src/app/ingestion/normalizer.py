from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Callable
from typing import Optional

from ..models import BudgetBand, Restaurant


@dataclass(frozen=True)
class ColumnMapping:
    name: str
    location: str
    cuisines: str
    rating: Optional[str]
    cost: Optional[str]


def _norm_str(v: Any) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    return re.sub(r"\s+", " ", s)


def _parse_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, (int, float)) and not (isinstance(v, float) and (v != v)):  # NaN check
        return float(v)

    s = _norm_str(v)
    if not s:
        return None

    # Strip currency symbols/commas and pick first numeric token.
    s = s.replace(",", "")
    m = re.search(r"-?\d+(\.\d+)?", s)
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def _parse_cuisines(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, list):
        items = [str(x) for x in v if str(x).strip()]
    else:
        s = _norm_str(v)
        if not s:
            return []
        items = [p.strip() for p in s.split(",") if p.strip()]
    # normalize
    return [re.sub(r"\s+", " ", c).lower() for c in items]


def _stable_restaurant_id(*, name: str, location: str, cuisines: list[str], estimated_cost: Optional[float]) -> str:
    payload = {
        "name": name.lower(),
        "location": location.lower(),
        "cuisines": cuisines,
        "estimated_cost": estimated_cost if estimated_cost is not None else None,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:12]


def infer_column_mapping(columns: list[str]) -> ColumnMapping:
    """
    Infer a mapping from dataset columns to canonical fields.
    This is heuristic-based to avoid assuming specific schema names.
    """
    cols_lower = {c.lower(): c for c in columns}

    def pick(*candidates: str) -> Optional[str]:
        for cand in candidates:
            if cand in cols_lower:
                return cols_lower[cand]
        return None

    name = pick("name", "restaurant_name", "restaurant", "res_name")
    location = pick("location", "city", "locality", "area", "address")
    cuisines = pick("cuisines", "cuisine", "cuisine_style", "food_type")
    rating = pick(
        "rate",
        "rating",
        "aggregate_rating",
        "zomato_rating",
        "user_rating",
        "rating_aggregate",
    )
    cost = pick(
        "estimated_cost",
        "cost",
        "average_cost_for_two",
        "cost_for_two",
        "approx_cost(for two people)",
        "price",
    )

    missing_required = [k for k, v in {"name": name, "location": location, "cuisines": cuisines}.items() if v is None]
    if missing_required:
        raise ValueError(
            "Unable to infer required columns. "
            f"Missing: {missing_required}. "
            f"Observed columns: {columns}"
        )

    return ColumnMapping(name=name, location=location, cuisines=cuisines, rating=rating, cost=cost)


def derive_budget_band(estimated_cost: Optional[float], *, low_max: float, medium_max: float) -> BudgetBand:
    if estimated_cost is None:
        return BudgetBand.unknown
    if estimated_cost <= low_max:
        return BudgetBand.low
    if estimated_cost <= medium_max:
        return BudgetBand.medium
    return BudgetBand.high


def normalize_row(
    row: dict[str, Any],
    *,
    mapping: ColumnMapping,
    low_max: float,
    medium_max: float,
    extra_metadata_columns: Optional[Callable[[dict[str, Any]], dict[str, Any]]] = None,
) -> Optional[Restaurant]:
    name = _norm_str(row.get(mapping.name))
    location = _norm_str(row.get(mapping.location))
    cuisines = _parse_cuisines(row.get(mapping.cuisines))

    if not name or not location:
        return None

    rating_val = _parse_float(row.get(mapping.rating)) if mapping.rating else None
    rating = float(rating_val) if rating_val is not None else 0.0
    # clamp rating to [0, 5]
    if rating < 0:
        rating = 0.0
    if rating > 5:
        rating = 5.0

    estimated_cost = _parse_float(row.get(mapping.cost)) if mapping.cost else None
    budget_band = derive_budget_band(estimated_cost, low_max=low_max, medium_max=medium_max)

    metadata: dict[str, Any] = {}
    if extra_metadata_columns:
        metadata = extra_metadata_columns(row) or {}

    rid = _stable_restaurant_id(
        name=name,
        location=location,
        cuisines=cuisines,
        estimated_cost=estimated_cost,
    )

    return Restaurant(
        id=rid,
        name=name,
        location=location,
        cuisines=cuisines,
        rating=rating,
        estimated_cost=estimated_cost,
        budget_band=budget_band,
        metadata=metadata,
    )

