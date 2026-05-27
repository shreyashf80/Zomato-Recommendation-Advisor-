#!/usr/bin/env python3
"""CLI to run recommendations with Groq LLM."""
from __future__ import annotations

import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app.models import UserPreferences  # noqa: E402
from app.services import build_use_case_from_settings  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Get restaurant recommendations via Groq.")
    parser.add_argument("--location", required=True)
    parser.add_argument("--budget", choices=["low", "medium", "high"], required=True)
    parser.add_argument("--cuisine", required=True)
    parser.add_argument("--min-rating", type=float, default=3.5)
    parser.add_argument("--additional", default=None, help="Free-text preferences")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    prefs = UserPreferences(
        location=args.location,
        budget=args.budget,
        cuisine=args.cuisine,
        min_rating=args.min_rating,
        additional_preferences=args.additional,
        top_k=args.top_k,
    )

    use_case = build_use_case_from_settings()
    response = use_case.execute(prefs)
    print(json.dumps(response.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
