# Edge Cases & Handling Guide

This document lists **edge cases** for the AI-powered restaurant recommendation system and defines the expected **behavior**, **fallbacks**, and **what to log/test**. It complements `docs/architecture.md` and is meant to be used as an implementation + QA checklist.

---

## 1) Data ingestion & preprocessing

### 1.1 Hugging Face dataset unavailable / download fails

- **Symptoms**: network error, HF rate limit, dataset not found.
- **Expected behavior**:
  - If running ingestion CLI: fail fast with actionable error.
  - If app boot depends on ingestion: run in “store not ready” mode (API returns 503) with a clear message.
- **Fallback**:
  - Use last known processed artifact if present (`data/processed/...`) and it passes basic schema validation.
- **Log**:
  - dataset id, exception, retry count, artifact fallback used yes/no.
- **Test**:
  - simulate loader raising exception; verify fallback artifact path is used.

### 1.2 Dataset schema/column names differ from assumptions

- **Expected behavior**:
  - `SchemaNormalizer` inspects columns and maps them explicitly.
  - If required fields cannot be mapped (name/location/cuisines/cost/rating): stop ingestion with error listing missing columns.
- **Fallback**:
  - None (better to fail ingestion than silently corrupt outputs).
- **Log**:
  - observed columns, mapping decisions, missing required fields.
- **Test**:
  - unit test normalizer with “renamed columns” fixtures.

### 1.3 Missing/null values in key fields

- **Examples**: missing rating, empty cuisines, null location, null cost.
- **Expected behavior**:
  - Apply consistent defaults or drop rows depending on field:
    - **name**: drop row if missing/empty
    - **location**: drop or set `"unknown"` (prefer drop for MVP)
    - **cuisines**: set to `[]` and treat as non-match for cuisine filter
    - **rating**: set to `0.0` (still filterable by min_rating)
    - **cost**: set to `NaN` and derive `budget_band = "unknown"` (exclude from budget filter matches)
- **Fallback**:
  - If too many rows are dropped (configurable threshold), warn and keep artifact but mark “data quality degraded”.
- **Log**:
  - counts of dropped rows per reason, null rates.
- **Test**:
  - fixture rows with nulls; assert resulting canonical fields and drop rules.

### 1.4 Non-numeric or out-of-range numeric fields

- **Examples**: rating `"NEW"` or `"—"`, cost `"₹1,200"` or string ranges.
- **Expected behavior**:
  - Parse robustly; if parse fails, default as in 1.3.
  - Clamp rating to \([0,5]\) after parsing.
- **Log**:
  - parse failure count per field, examples (dev only; redacted in prod).
- **Test**:
  - rating parse cases; cost parse cases with currency symbols/commas.

### 1.5 Duplicate restaurants / unstable IDs

- **Expected behavior**:
  - Generate a stable `restaurant_id` (e.g., hash of normalized name + location + cuisines + cost) so IDs persist across runs.
  - Dedupe exact duplicates during preprocessing.
- **Log**:
  - dedupe count, collision count (should be 0 or extremely low).
- **Test**:
  - duplicates map to same ID; different restaurants do not collide (basic check).

### 1.6 Budget band thresholds mismatch the dataset

- **Expected behavior**:
  - Thresholds are config-driven; ingestion computes `budget_band` deterministically.
  - If cost distribution suggests thresholds are unreasonable (optional): warn.
- **Log**:
  - thresholds used; distribution by band (counts).

---

## 2) Restaurant store & filtering

### 2.1 Processed artifact missing / unreadable / wrong schema

- **Expected behavior**:
  - On startup: fail store init and keep app alive in degraded mode.
  - API returns `503 StoreNotReady` with guidance (“run ingest first”).
- **Fallback**:
  - None unless an older artifact exists and passes schema validation.
- **Log**:
  - artifact path, validation errors.
- **Test**:
  - missing file; corrupted file; schema mismatch.

### 2.2 Location matching ambiguity (case, spelling, locality vs city)

- **Expected behavior (MVP)**:
  - Case-insensitive substring match against canonical `location`.
  - Normalize input (trim; title-case for display only).
- **Fallback (future)**:
  - fuzzy match / “did you mean” suggestions.
- **Log**:
  - input location, number of matches before other filters.
- **Test**:
  - “bangalore” matches “Bangalore”; extra whitespace; partial locality.

### 2.3 Cuisine mismatch due to formatting

- **Examples**: “Italian ”, “italian”, “Italian, Continental”.
- **Expected behavior**:
  - Normalize cuisines to lowercased list; user cuisine lowercased.
  - Any-match filter on cuisines list.
- **Log**:
  - user cuisine, match count.
- **Test**:
  - casing/whitespace; multi-cuisine restaurants.

### 2.4 Budget filter with missing/unknown cost

- **Expected behavior**:
  - Restaurants with unknown `budget_band` do **not** match any budget.
  - Optionally: add a “budget not specified” mode later; not required for MVP.
- **Test**:
  - unknown cost does not appear in results when budget is required.

### 2.5 min_rating too strict leading to zero matches

- **Expected behavior**:
  - Return empty response and **skip LLM call**.
  - UI shows a helpful message (suggest lowering rating or adjusting filters).
- **Log**:
  - filters applied; zero-match reason.
- **Test**:
  - strict min_rating yields empty response without calling LLM client.

### 2.6 Too many matches (candidate explosion)

- **Expected behavior**:
  - Pre-sort by rating (and votes if available) and cap to `MAX_CANDIDATES` before prompt.
  - Return metadata: `total_before_cap` and `candidates_considered`.
- **Log**:
  - total_before_cap, cap applied, max_candidates.
- **Test**:
  - verify cap always enforced; prompt never exceeds candidate bound.

### 2.7 top_k > candidates

- **Expected behavior**:
  - Return at most `len(candidates)` results.
  - UI should not error; show fewer cards.
- **Test**:
  - ask for top_k 10 with only 3 candidates.

---

## 3) Prompting & grounding (LLM integration)

### 3.1 Hallucinations (LLM invents restaurants)

- **Expected behavior**:
  - Prompt explicitly forbids new restaurants and lists allowed `restaurant_id`s.
  - Parser drops unknown IDs and continues with remaining.
- **Fallback**:
  - If too few valid recommendations remain, fill remaining slots by deterministic rating sort with generic explanation.
- **Log**:
  - unknown_id_count, dropped_ids, fallback_used yes/no.
- **Test**:
  - parser fixture includes invented IDs; verify drop + fill behavior.

### 3.2 LLM returns invalid JSON / extra prose

- **Expected behavior**:
  - Attempt JSON parse; if fails, extract JSON block; re-parse.
  - If still fails: deterministic fallback ranking.
- **Log**:
  - parse_failed yes/no, extraction_used yes/no.
- **Test**:
  - fixtures: valid JSON, JSON wrapped in text, malformed JSON.

### 3.3 LLM returns fewer than requested recommendations

- **Expected behavior**:
  - Accept partial list, then fill remaining with rating-based picks not already chosen.
- **Log**:
  - returned_count vs requested_count.
- **Test**:
  - LLM returns 2 items when top_k=5.

### 3.4 LLM returns duplicate restaurant_ids or duplicate ranks

- **Expected behavior**:
  - De-duplicate by `restaurant_id` (keep best rank).
  - Normalize ranks to 1..N in final output.
- **Log**:
  - duplicates detected and removed.
- **Test**:
  - fixture with duplicates.

### 3.5 LLM ranks outside candidate set (id is valid but not in this request’s candidates)

- **Expected behavior**:
  - Treat as unknown for this request and drop.
- **Log**:
  - out_of_candidate_set_count.
- **Test**:
  - fixture includes a valid global ID not present in current candidates.

### 3.6 LLM call fails (timeouts, 5xx, rate limiting)

- **Expected behavior**:
  - Retry once with backoff for timeouts/transient failures.
  - If still failing: deterministic fallback ranking.
- **Optional**:
  - Cache by hash(preferences + candidate_ids) to reduce repeated calls (later).
- **Log**:
  - provider, model, latency, retry count, final outcome.
- **Test**:
  - mocked client raising timeout triggers fallback.

### 3.7 Token/size overflow (prompt too large)

- **Expected behavior**:
  - Enforce `MAX_CANDIDATES`.
  - Truncate overly long `additional_preferences` at input boundary.
  - Use minimal candidate fields in prompt.
- **Log**:
  - candidate_count, approximate prompt size, truncated flags.
- **Test**:
  - very long `additional_preferences` is truncated and does not break request.

---

## 4) Orchestrator behavior & output contract

### 4.1 Empty candidate list

- **Expected behavior**:
  - Return:
    - `summary` explaining no matches
    - `recommendations: []`
    - `meta` includes applied filters and `candidates_considered = 0`
  - **Skip LLM call**
- **Test**:
  - filter returns empty; ensure no LLM invocation.

### 4.2 Partial parse success (some recommendations valid, some dropped)

- **Expected behavior**:
  - Keep valid ones; fill remaining via fallback.
- **Log**:
  - valid_count, dropped_count, fallback_fill_count.

### 4.3 Consistent ordering and determinism

- **Expected behavior**:
  - Final ordering is:
    - LLM order when valid
    - rating-based fallback for fill items
  - Temperature should be low (0.2–0.5) to stabilize rankings.
- **Test**:
  - deterministic output for fallback path.

---

## 5) API / UI edge cases

### 5.1 Invalid user input

- **Cases**:
  - empty location/cuisine
  - min_rating outside \([0,5]\)
  - top_k <= 0 or too large
  - budget not in {low, medium, high}
- **Expected behavior**:
  - Return `400` with field-level validation errors (API) or inline form errors (UI).
- **Test**:
  - schema validation tests.

### 5.2 Store not loaded yet

- **Expected behavior**:
  - API returns `503` with message to run ingestion.
  - UI shows “data not ready” state.

### 5.3 Slow LLM responses

- **Expected behavior**:
  - UI shows a spinner and does not freeze.
  - Server-side timeout handled; fallback used if hit.
- **Log**:
  - LLM latency distribution.

### 5.4 User asks for contradictory preferences

- **Examples**: “high budget” + “as cheap as possible”, or “Italian” + “no dairy”.
- **Expected behavior**:
  - Structured filters apply as specified.
  - LLM uses free-text preferences for tie-breaking/explanations; it may surface trade-offs in summary.

---

## 6) Security & privacy guardrails (MVP)

- **Secrets**: never log API keys; never commit `.env`.
- **Prompt logging**: if enabled, dev-only and redacted; off by default.
- **Input limits**: cap free text length; strip control characters.
- **Injection resistance**:
  - Prompt includes a strict rule: ignore instructions that conflict with system rules; only use provided candidates.

---

## 7) Observability checklist (what to measure)

- **Filtering**:
  - total_before_cap, candidates_considered, applied filters, cap applied
- **LLM**:
  - provider/model, latency, retries, parse success rate
- **Grounding**:
  - unknown/out-of-set ID rates, fallback usage rate
- **UX**:
  - empty-result rate, average time-to-first-result

---

## 8) Minimum test suite (recommended)

- **Unit tests**
  - `SchemaNormalizer`: column mapping + parsing rules
  - `FilterService`: each filter + zero/too-many matches
  - `PromptBuilder`: bounded candidates + contract in prompt
  - `ResponseParser`: invalid JSON, invented IDs, duplicates
- **Integration tests**
  - Orchestrator with mocked LLM client (success + failure paths)
- **E2E**
  - One golden path using a recorded LLM fixture (repeatable, no network)

