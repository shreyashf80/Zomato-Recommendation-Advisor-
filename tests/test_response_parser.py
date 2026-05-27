from __future__ import annotations

import json

import pytest

from app.services.response_parser import ResponseParser


def test_parse_valid_json() -> None:
    raw = json.dumps(
        {
            "summary": "Nice picks.",
            "recommendations": [
                {"restaurant_id": "a", "rank": 1, "explanation": "Great fit."},
                {"restaurant_id": "b", "rank": 2, "explanation": "Also good."},
            ],
        }
    )
    parsed = ResponseParser().parse(raw, allowed_ids={"a", "b", "c"})
    assert parsed.summary == "Nice picks."
    assert len(parsed.recommendations) == 2
    assert parsed.recommendations[0].restaurant_id == "a"


def test_parse_drops_unknown_ids() -> None:
    raw = json.dumps(
        {
            "recommendations": [
                {"restaurant_id": "x", "rank": 1, "explanation": "Hallucinated."},
                {"restaurant_id": "a", "rank": 2, "explanation": "Real."},
            ],
        }
    )
    parsed = ResponseParser().parse(raw, allowed_ids={"a"})
    assert len(parsed.recommendations) == 1
    assert parsed.recommendations[0].restaurant_id == "a"


def test_parse_invalid_raises() -> None:
    with pytest.raises(ValueError):
        ResponseParser().parse("<<<", allowed_ids={"a"})
