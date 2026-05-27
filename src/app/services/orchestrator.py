from __future__ import annotations

import time
from typing import Optional

from app.services.logging import logger
from ..config import Settings, get_settings
from ..data.repository import RestaurantRepository
from ..models import RecommendationResponse, ResponseMeta, UserPreferences
from .llm_factory import create_llm_client
from .filter_service import FilterService
from .llm_client import LLMClient, LLMClientError
from .prompt_builder import PromptBuilder
from .recommendation_merger import RecommendationMerger
from .response_parser import ResponseParser

_FILTER_KEYS = ("location", "budget", "cuisine", "min_rating")


class RecommendRestaurantsUseCase:
    def __init__(
        self,
        repository: RestaurantRepository,
        filter_service: FilterService,
        llm_client: LLMClient,
        *,
        prompt_builder: Optional[PromptBuilder] = None,
        response_parser: Optional[ResponseParser] = None,
        merger: Optional[RecommendationMerger] = None,
    ) -> None:
        self._repository = repository
        self._filter_service = filter_service
        self._llm_client = llm_client
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._response_parser = response_parser or ResponseParser()
        self._merger = merger or RecommendationMerger()

    def execute(self, preferences: UserPreferences) -> RecommendationResponse:
        start_time = time.time()
        
        # Step 1: validate (Pydantic validates on construction; re-validate via model_dump roundtrip)
        prefs = UserPreferences.model_validate(preferences.model_dump())
        logger.info(
            f"Starting recommendation search: location='{prefs.location}', "
            f"cuisine='{prefs.cuisine}', budget='{prefs.budget}', "
            f"min_rating={prefs.min_rating}, top_k={prefs.top_k}, "
            f"has_additional_prefs={prefs.additional_preferences is not None}"
        )

        # Step 2: filter candidates
        filter_result = self._filter_service.filter(prefs, self._repository)
        filters_applied = [k for k in _FILTER_KEYS if k in filter_result.applied_filters]
        logger.info(
            f"Deterministic filtering complete. Candidates considered: {filter_result.total_before_cap}. "
            f"Filtered candidates capped to: {len(filter_result.candidates)}. "
            f"Applied filters: {filters_applied}."
        )

        meta = ResponseMeta(
            candidates_considered=filter_result.total_before_cap,
            filters_applied=filters_applied,
        )

        # Step 3: short-circuit on empty
        if not filter_result.candidates:
            logger.warning("No candidate restaurants matched criteria. Skipping LLM request.")
            return RecommendationResponse(
                summary=(
                    "No restaurants matched your filters. "
                    "Try relaxing location, budget, cuisine, or minimum rating."
                ),
                recommendations=[],
                meta=meta,
            )

        allowed_ids = {r.id for r in filter_result.candidates}

        # Steps 4–7: prompt → LLM → parse → merge (with fallback)
        prompt = self._prompt_builder.build(prefs, filter_result.candidates)
        prompt_bytes = len(prompt.system.encode('utf-8')) + len(prompt.user.encode('utf-8'))
        approx_tokens = prompt_bytes // 4
        logger.info(
            f"Constructed LLM prompt. Prompt size: {prompt_bytes} bytes "
            f"(approx {approx_tokens} tokens)."
        )

        fallback_used = False
        llm_start = time.time()

        try:
            logger.info("Sending request to LLM client...")
            raw = self._llm_client.complete(prompt)
            llm_latency = time.time() - llm_start
            logger.info(f"LLM returned successfully. Call completed in {llm_latency:.2f}s.")
            
            parsed = self._response_parser.parse(raw, allowed_ids=allowed_ids)
            logger.info(
                f"Successfully parsed LLM response. Valid candidates returned: {len(parsed.recommendations)}."
            )
            
            recommendations = self._merger.merge(
                parsed,
                filter_result.candidates,
                top_k=prefs.top_k,
            )
            summary = parsed.summary
        except (LLMClientError, ValueError, KeyError, TypeError) as exc:
            llm_latency = time.time() - llm_start
            logger.warning(
                f"LLM processing or response parsing failed after {llm_latency:.2f}s: {exc}. "
                "Triggering rating-based fallback resolver."
            )
            fallback_used = True
            recommendations = self._merger.fallback(
                filter_result.candidates,
                top_k=prefs.top_k,
            )
            summary = (
                f"Showing top {len(recommendations)} matches by rating "
                "(personalized explanations unavailable)."
            )

        meta.fallback_used = fallback_used
        total_latency = time.time() - start_time
        logger.info(
            f"Recommendation execution finished in {total_latency:.2f}s. "
            f"Fallback activated: {fallback_used}."
        )
        
        return RecommendationResponse(
            summary=summary,
            recommendations=recommendations,
            meta=meta,
        )



def build_use_case(
    repository: RestaurantRepository,
    llm_client: LLMClient,
    *,
    max_candidates: int = 30,
) -> RecommendRestaurantsUseCase:
    return RecommendRestaurantsUseCase(
        repository=repository,
        filter_service=FilterService(max_candidates=max_candidates),
        llm_client=llm_client,
    )


def build_use_case_from_settings(
    settings: Optional[Settings] = None,
    *,
    repository: Optional[RestaurantRepository] = None,
) -> RecommendRestaurantsUseCase:
    """Wire repository + Groq (or mock) LLM from application settings."""
    cfg = settings or get_settings()
    repo = repository or RestaurantRepository.from_parquet(cfg.data_path)
    return build_use_case(
        repo,
        create_llm_client(cfg),
        max_candidates=cfg.max_candidates,
    )
