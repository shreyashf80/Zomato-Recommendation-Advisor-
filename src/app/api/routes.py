from __future__ import annotations

import re
from fastapi import APIRouter, HTTPException, Request

from app.api.schemas import RecommendationResponse, UserPreferences

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/metadata/locations", response_model=list[str])
def get_locations(request: Request) -> list[str]:
    repo = getattr(request.app.state, "repository", None)
    if repo is None:
        raise HTTPException(status_code=503, detail="Repository not initialized")
    
    try:
        all_rests = repo.get_all()
        locations = sorted(list(set(r.location for r in all_rests)))
        return locations
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch locations: {exc}")


@router.get("/metadata/cuisines", response_model=list[str])
def get_cuisines(request: Request) -> list[str]:
    repo = getattr(request.app.state, "repository", None)
    if repo is None:
        raise HTTPException(status_code=503, detail="Repository not initialized")
        
    try:
        all_rests = repo.get_all()
        raw_cuisines = set()
        for r in all_rests:
            for c in r.cuisines:
                raw_cuisines.add(c)
                
        cleaned = set()
        for c in raw_cuisines:
            matches = re.findall(r"'([^']*)'", c)
            if matches:
                for m in matches:
                    if m.strip():
                        cleaned.add(m.strip().lower())
            else:
                for part in re.split(r"[,;]", c):
                    if part.strip():
                        cleaned.add(part.strip().lower())
                        
        cuisines = sorted(list(c for c in cleaned if c and c != "[]"))
        return cuisines
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cuisines: {exc}")


@router.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(request: Request, preferences: UserPreferences) -> RecommendationResponse:
    use_case = getattr(request.app.state, "use_case", None)
    if use_case is None:
        raise HTTPException(status_code=503, detail="Recommendation engine not initialized")
    
    try:
        result = use_case.execute(preferences)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Orchestration execution failed: {exc}")
