from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Optional

import pandas as pd

from ..config import Settings
from ..models import Restaurant
from .loader import load_hf_dataset, maybe_set_hf_home
from .normalizer import ColumnMapping, infer_column_mapping, normalize_row


@dataclass(frozen=True)
class IngestReport:
    dataset_id: str
    split: str
    rows_total: int
    rows_dropped_missing_required: int
    rows_written: int
    mapping: ColumnMapping
    null_rates: dict[str, float]
    distinct_counts: dict[str, int]


def _ensure_parent_dir(path: str) -> None:
    Path(path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)


def _restaurants_to_dataframe(restaurants: list[Restaurant]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for r in restaurants:
        rows.append(
            {
                "id": r.id,
                "name": r.name,
                "location": r.location,
                "cuisines": r.cuisines,
                "rating": r.rating,
                "estimated_cost": r.estimated_cost,
                "budget_band": r.budget_band.value,
                # JSON string avoids Parquet empty-struct write errors.
                "metadata_json": json.dumps(r.metadata or {}, ensure_ascii=False),
            }
        )
    return pd.DataFrame(rows)


def run_ingestion(settings: Settings) -> IngestReport:
    maybe_set_hf_home(settings.hf_home or "./data/raw/hf_cache")

    loaded = load_hf_dataset(settings.dataset_id)
    ds = loaded.dataset

    columns = list(ds.column_names)
    mapping = infer_column_mapping(columns)

    restaurants: list[Restaurant] = []
    dropped = 0

    # Iterate through dataset rows without assuming pandas conversion will work for all schemas.
    def _extra_metadata(row: dict[str, Any]) -> dict[str, Any]:
        meta: dict[str, Any] = {}
        for key in ("votes", "address", "rest_type", "url"):
            if key in row and row[key] not in (None, ""):
                meta[key] = row[key]
        return meta

    for row in ds:
        r = normalize_row(
            row,
            mapping=mapping,
            low_max=settings.budget_low_max,
            medium_max=settings.budget_medium_max,
            extra_metadata_columns=_extra_metadata,
        )
        if r is None:
            dropped += 1
            continue
        restaurants.append(r)

    # De-dupe by stable id (keeps first)
    deduped: dict[str, Restaurant] = {}
    for r in restaurants:
        if r.id not in deduped:
            deduped[r.id] = r
    restaurants = list(deduped.values())

    df = _restaurants_to_dataframe(restaurants)

    # Data profile
    null_rates = {
        "location": float(df["location"].isna().mean()) if "location" in df else 1.0,
        "cuisines": float(df["cuisines"].isna().mean()) if "cuisines" in df else 1.0,
        "rating": float(df["rating"].isna().mean()) if "rating" in df else 1.0,
        "estimated_cost": float(df["estimated_cost"].isna().mean()) if "estimated_cost" in df else 1.0,
    }
    distinct_counts = {
        "locations": int(df["location"].nunique(dropna=True)) if "location" in df else 0,
        "cuisines_tokens": int(
            pd.Series([c for cs in df["cuisines"].tolist() for c in (cs or [])]).nunique(dropna=True)
        )
        if "cuisines" in df
        else 0,
    }

    # Persist
    out_path = Path(settings.data_path)
    _ensure_parent_dir(str(out_path))
    df.to_parquet(out_path, index=False)

    # Write a small sidecar report (useful for debugging and metadata endpoints later).
    report_path = out_path.with_suffix(".report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "dataset_id": settings.dataset_id,
                "split": loaded.split,
                "rows_total": int(ds.num_rows),
                "rows_dropped_missing_required": int(dropped),
                "rows_written": int(len(df)),
                "column_mapping": mapping.__dict__,
                "null_rates": null_rates,
                "distinct_counts": distinct_counts,
                "budget_thresholds": {
                    "low_max": settings.budget_low_max,
                    "medium_max": settings.budget_medium_max,
                },
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    return IngestReport(
        dataset_id=settings.dataset_id,
        split=loaded.split,
        rows_total=int(ds.num_rows),
        rows_dropped_missing_required=int(dropped),
        rows_written=int(len(df)),
        mapping=mapping,
        null_rates=null_rates,
        distinct_counts=distinct_counts,
    )


def format_report_for_console(report: IngestReport, *, output_path: str) -> str:
    return "\n".join(
        [
            "Ingestion complete",
            f"- dataset_id: {report.dataset_id}",
            f"- split: {report.split}",
            f"- rows_total: {report.rows_total}",
            f"- rows_dropped_missing_required: {report.rows_dropped_missing_required}",
            f"- rows_written: {report.rows_written}",
            f"- output: {output_path}",
            f"- mapping: {report.mapping.__dict__}",
            f"- null_rates: {report.null_rates}",
            f"- distinct_counts: {report.distinct_counts}",
        ]
    )

