from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from .restaurant import Restaurant


class Recommendation(BaseModel):
    restaurant: Restaurant
    rank: int = Field(ge=1)
    explanation: str


class ResponseMeta(BaseModel):
    candidates_considered: int = 0
    filters_applied: list[str] = Field(default_factory=list)
    fallback_used: bool = False


class RecommendationResponse(BaseModel):
    summary: Optional[str] = None
    recommendations: list[Recommendation] = Field(default_factory=list)
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
