from __future__ import annotations

from enum import Enum
from typing import Any
from typing import Optional

from pydantic import BaseModel, Field


class BudgetBand(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    unknown = "unknown"


class Restaurant(BaseModel):
    id: str
    name: str
    location: str
    cuisines: list[str] = Field(default_factory=list)
    rating: float = 0.0
    estimated_cost: Optional[float] = None
    budget_band: BudgetBand = BudgetBand.unknown
    metadata: dict[str, Any] = Field(default_factory=dict)

