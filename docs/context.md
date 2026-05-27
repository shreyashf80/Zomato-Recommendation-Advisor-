# Zomato Milestone — Project Context

## Overview

Build an **AI-powered restaurant recommendation service** inspired by Zomato. The system combines structured restaurant data with a **Large Language Model (LLM)** to produce personalized, human-like suggestions from user preferences.

---

## Objective

Design and implement an application that:

1. Accepts user preferences (location, budget, cuisine, ratings, and more)
2. Uses a real-world restaurant dataset
3. Leverages an LLM for personalized, natural-language recommendations
4. Presents clear, useful results to the user

---

## Dataset

| Property | Value |
|----------|--------|
| **Source** | Hugging Face |
| **URL** | https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation |
| **Relevant fields** | Restaurant name, location, cuisine, cost, rating, and related metadata |

---

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face
- Extract fields needed for filtering and display: name, location, cuisine, cost, rating, etc.

### 2. User Input

Collect preferences from the user:

| Preference | Examples |
|------------|----------|
| **Location** | Delhi, Bangalore |
| **Budget** | low, medium, high |
| **Cuisine** | Italian, Chinese |
| **Minimum rating** | Numeric threshold |
| **Additional** | family-friendly, quick service, etc. |

### 3. Integration Layer

- Filter and prepare restaurant records that match user input
- Pass structured candidate results into an LLM prompt
- Design a prompt so the LLM can reason over and rank options

### 4. Recommendation Engine (LLM)

The LLM should:

- **Rank** restaurants by fit to preferences
- **Explain** why each recommendation matches
- **Optionally** summarize the overall set of choices

### 5. Output Display

Present top recommendations in a user-friendly format. Each item should include:

| Field | Description |
|-------|-------------|
| Restaurant Name | From dataset |
| Cuisine | From dataset |
| Rating | From dataset |
| Estimated Cost | From dataset |
| AI-generated explanation | From LLM |

---

## High-Level Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Hugging    │     │  Filter / Prep   │     │  LLM Prompt +   │
│  Face       │────▶│  (user prefs)    │────▶│  Ranking        │
│  Dataset    │     │                  │     │                 │
└─────────────┘     └──────────────────┘     └────────┬────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  User-facing    │
                                               │  Results UI     │
                                               └─────────────────┘
```

---

## Functional Requirements (Checklist)

- [ ] Ingest Zomato dataset from Hugging Face
- [ ] Preprocess and expose structured fields
- [ ] Collect user preferences (location, budget, cuisine, min rating, extras)
- [ ] Filter restaurants by structured criteria before LLM call
- [ ] Build LLM prompt with filtered candidates and user context
- [ ] Generate ranked recommendations with explanations
- [ ] Display results with name, cuisine, rating, cost, and AI explanation

---

## Non-Functional Considerations

- **Data quality**: Handle missing or inconsistent fields during preprocessing
- **Prompt design**: Keep prompts focused so the LLM ranks from real candidates, not hallucinated venues
- **Latency**: Batch or limit candidate set sent to the LLM if the dataset slice is large
- **Cost**: Prefer smaller candidate lists post-filter to reduce token usage

---

## Success Criteria

The milestone is complete when a user can enter preferences, receive a ranked list of real restaurants from the dataset, and read clear LLM-written reasons why each place fits their criteria.

---

## Source Document

This context is derived from `docs/problemStatement.txt` in the Zomato_Milestone project.
