from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from .user_preferences import BudgetLevel, UserPreferences


class FilterCriteria(BaseModel):
    location: str
    budget: BudgetLevel
    cuisine: str
    min_rating: float = Field(ge=0.0, le=5.0)

    @classmethod
    def from_preferences(cls, preferences: UserPreferences) -> "FilterCriteria":
        return cls(
            location=preferences.location_normalized,
            budget=preferences.budget,
            cuisine=preferences.cuisine_normalized,
            min_rating=preferences.min_rating,
        )

    @property
    def location_normalized(self) -> str:
        return self.location.strip().lower()

    @property
    def cuisine_normalized(self) -> str:
        return self.cuisine.strip().lower()
