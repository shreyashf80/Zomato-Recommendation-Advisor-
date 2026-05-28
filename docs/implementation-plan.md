# Implementation Plan (Phase-wise)

This plan operationalizes the architecture described in `docs/architecture.md` and the workflow in `docs/context.md` into **phases** with clear deliverables and exit criteria.

## Guiding principles (from architecture)

- **Grounding first**: recommendations must come only from the provided Zomato dataset candidates (no fabricated restaurants).
- **Filter before generate**: apply deterministic structured filters before any LLM call.
- **Bounded prompting**: cap candidate restaurants passed to the LLM (e.g., 20–50; recommended default \(= 30\)).
- **Structured + generative**: dataset fields are the source of truth; LLM ranks + explains.
- **Single-tenant MVP**: no auth required for the milestone.

---

## Phase 0 — Scaffolding + baseline decisions [STATUS: COMPLETED]

### Deliverables

- Repository structure aligned to architecture (recommended):
  - `docs/`, `data/raw/`, `data/processed/`, `src/app/`, `tests/`, `scripts/`
- `.env.example` capturing:
  - `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`
  - `DATA_PATH`, `MAX_CANDIDATES`
  - `BUDGET_LOW_MAX`, `BUDGET_MEDIUM_MAX` (or equivalent thresholds)
  - `CORS_ORIGINS` (comma-separated list of allowed origins)
- A minimal runnable entrypoint:
  - `src/app/main.py` (even if it only shows a placeholder screen / health endpoint)

### Key decision (Selected)

- **Presentation Layer Choice**: Option B (FastAPI backend + React Vite frontend) is selected and implemented to follow Zomato's brand aesthetics and single-page, center-focused responsive layout rules. Streamlit is deprecated.

### Exit criteria

- App starts without ingest/LLM configured (clear error messages if missing config).
- No secrets committed; `.env.example` is present.

---

## Phase 1 — Data ingestion pipeline (offline / startup) [STATUS: COMPLETED]

Implements the “Data Ingestion Pipeline” components:
`DatasetLoader` → `SchemaNormalizer` → `Preprocessor` → `PersistenceWriter`.

### Deliverables

- Canonical domain model `Restaurant`:
  - `id`, `name`, `location`, `cuisines[]`, `rating`, `estimated_cost`, `budget_band`, optional `metadata`
- Ingestion modules:
  - `src/app/ingestion/loader.py`
  - `src/app/ingestion/normalizer.py`
  - `src/app/ingestion/pipeline.py`
- CLI entry for ingest:
  - `scripts/ingest.py` (or `python -m app.ingest`) writing to `data/processed/`
- Processed artifact:
  - Parquet (simple) or SQLite (queryable). Either is acceptable.

### Implementation notes

- On first integration, **inspect actual dataset column names** and map them in `SchemaNormalizer` (do not assume).
- Normalize:
  - cuisines → `list[str]` (lowercased, split on commas)
  - location → consistent casing (case-insensitive matching)
  - cost → numeric `estimated_cost`
  - `budget_band` derived from thresholds

### Exit criteria

- Ingest runs end-to-end and produces a processed artifact.
- Output includes a small “data profile” log:
  - total rows ingested
  - null rates for key fields (location/cuisines/rating/cost)
  - a count of distinct locations/cuisines (for future autocomplete)

---

## Phase 2 — Restaurant store + deterministic filtering [STATUS: COMPLETED]

Implements “Restaurant Store & Repository” + “Filter Service”.

### Deliverables

- `src/app/data/repository.py`:
  - `get_all()`, `filter(criteria)`, `get_by_ids(ids)`
- Filter criteria aligned to `UserPreferences`:
  - location, budget, cuisine, min_rating
  - `additional_preferences` is **not** a structural filter; it is forwarded to the LLM
- `src/app/services/filter_service.py`:
  - returns `candidates`, `total_before_cap`, `applied_filters`
  - pre-sort candidates by rating (and votes if available)
  - cap to `MAX_CANDIDATES` before LLM

### Edge case behavior

- If **zero matches** after hard filters: return empty response and **skip the LLM call**.

### Exit criteria

- Unit tests for each filter dimension and candidate-capping behavior.

---

## Phase 3 — Domain orchestration (use case) [STATUS: COMPLETED]

Implements “Recommendation Orchestrator” and DTOs.

### Deliverables

- `src/app/models/`:
  - `UserPreferences` (validation: required fields, `min_rating` in \([0,5]\))
  - `Recommendation`, `RecommendationResponse`
- `src/app/services/orchestrator.py`:
  - `RecommendRestaurantsUseCase.execute(preferences)` implements:
    1) validate preferences
    2) filter candidates
    3) short-circuit on empty
    4) build prompt
    5) call LLM
    6) parse response
    7) merge recommendations with dataset entities
    8) return response object for UI/API

### Exit criteria

- Integration test with mocked LLM produces stable output shape.

---

## Phase 4 — Prompt builder + LLM client + response parsing [STATUS: COMPLETED]

Implements “Integration Layer (Prompt Builder)” + “Recommendation Engine (LLM Client)” + “Response Parser”.

### Deliverables

- `src/app/services/prompt_builder.py`
  - system instructions:
    - act as restaurant advisor
    - **only** recommend from provided candidates
    - never invent restaurants
  - candidate block contains minimal fields and explicit allowed `restaurant_id`s
  - request a **JSON output contract**:

```json
{
  "summary": "Brief overview of the selection for this user.",
  "recommendations": [
    {
      "restaurant_id": "abc123",
      "rank": 1,
      "explanation": "Why this fits location, budget, cuisine, and extra preferences."
    }
  ]
}
```

- `src/app/services/llm_client.py`
  - provider-agnostic interface + **Groq** implementation (`GroqLLMClient`)
  - retry-once with backoff for timeouts (MVP)
- `src/app/services/llm_factory.py`
  - `create_llm_client(settings)` wires Groq from env (`GROQ_API_KEY`, `LLM_MODEL`)
- `src/app/services/response_parser.py`
  - JSON parse + schema validation
  - mitigation: extract JSON block if wrapped in text
  - drop unknown `restaurant_id`s from response
- `src/app/services/recommendation_merger.py` (or merger inside orchestrator)
  - join parsed output with `Restaurant` entities

### Fallback policy (required)

- If LLM fails or parsing fails:
  - return top-K by rating from filtered candidates
  - include a generic explanation (clearly marked as fallback in the response metadata)

### Exit criteria

- Snapshot test for prompt shape (bounded candidates, stable contract).
- Parser tests covering valid JSON, invalid JSON, unknown IDs, partial results.
- Manual run shows grounded recommendations (no fabricated restaurants).

---

## Phase 5 — API + presentation layer (React + FastAPI) [STATUS: COMPLETED]

Implement the user-facing experience using a React frontend communication with a FastAPI backend server.

### Deliverables

- **FastAPI Backend Services**:
  - `POST /api/v1/recommendations`: Accepts preference payloads, executes orchestrator, and returns JSON.
  - `GET /api/v1/health`: Checks application liveness.
  - `GET /api/v1/metadata/locations`: Returns distinct, sorted locations for frontend dropdown lists.
  - `GET /api/v1/metadata/cuisines`: Returns distinct, sorted cuisines for frontend dropdown lists.
  - `CORS_ORIGINS` CORS allowed origins configuration dynamically read from the environment variables.
- **React Frontend Application**:
  - Wide layout (`max-w-[1200px]`) containing a compact, responsive top filter grid panel (Location, Cuisine, Budget, Sliders, Special Requests, and Search button).
  - Dropdown fields dynamically loading from `/api/v1/metadata/*` endpoints on load.
  - Custom budget button selector (pills) and custom range sliders for rating and count inputs.
  - Responsive loading skeleton grid that mimics the cards' layout during active generation.
  - Results rendering of AI Verdict Summary banner and a multi-column restaurant cards grid (`grid-cols-1 md:grid-cols-2 lg:grid-cols-3` on desktop).
  - Vertical restaurant card components (image at top, details below) aligned to uniform heights.
  - Dynamic `VITE_API_BASE_URL` environment variable read at startup to connect to the custom backend server.

### Exit criteria

- The React application successfully requests metadata lists on start, handles loading states, and submits requests to the backend server, rendering results cleanly in a 3-column desktop layout.



---

## Phase 6 — Quality, observability, and hardening [STATUS: COMPLETED]

### Deliverables

- Logging:
  - filter counts, `candidates_considered`, applied filters
  - prompt size estimate (approx tokens/bytes)
  - LLM latency, parse success/failure
  - correlation id per request
- Input safety:
  - max length on `additional_preferences`
  - sanitize/trim strings
- Test coverage (minimum):
  - Unit: normalizer, filter service, prompt builder, parser
  - Integration: orchestrator with mocked LLM
  - E2E: one golden path with recorded fixture

### Exit criteria

- Failures degrade gracefully (fallback ranking), and errors are understandable to the user.

---

## Phase 7 — Packaging, deployment, and demo [STATUS: COMPLETED]

### Deliverables

- `README.md` with:
  - setup steps
  - ingest instructions
  - run instructions
  - environment variables
- Optional Docker packaging (especially for FastAPI + React split)

### Exit criteria

- Fresh setup flow works: ingest → run → generate recommendations.

---

## Suggested milestone path

- **Selected Path**: FastAPI + React (Phases 0–7) is implemented, enabling a separated REST API backend and a clean, responsive single-page web app using Zomato's brand design standards.


