from __future__ import annotations

from app.models import UserPreferences, RecommendationResponse

# Export the domain schemas for API consistency
__all__ = [
    "UserPreferences",
    "RecommendationResponse",
]
