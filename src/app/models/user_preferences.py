from __future__ import annotations

import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


BudgetLevel = Literal["low", "medium", "high"]


class UserPreferences(BaseModel):
    location: str
    budget: BudgetLevel
    cuisine: str
    min_rating: float = Field(ge=0.0, le=5.0)
    additional_preferences: Optional[str] = Field(default=None, max_length=500)
    top_k: int = Field(default=5, ge=1, le=50)

    @field_validator("location", "cuisine")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("must not be empty")
        return s

    @field_validator("additional_preferences")
    @classmethod
    def _trim_optional(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        s = v.strip()
        return s or None

    @property
    def location_normalized(self) -> str:
        return self.location.strip().lower()

    @property
    def cuisine_normalized(self) -> str:
        return re.sub(r"\s+", " ", self.cuisine.strip().lower())
