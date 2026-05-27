from __future__ import annotations

import argparse
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app.config import get_settings  # noqa: E402
from app.ingestion.pipeline import format_report_for_console, run_ingestion  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest and preprocess the Zomato HF dataset.")
    parser.add_argument(
        "--data-path",
        default=None,
        help="Override output path for processed parquet (defaults to DATA_PATH or ./data/processed/restaurants.parquet).",
    )
    args = parser.parse_args()

    settings = get_settings()
    if args.data_path:
        settings.data_path = args.data_path  # type: ignore[misc]

    report = run_ingestion(settings)
    print(format_report_for_console(report, output_path=settings.data_path))


if __name__ == "__main__":
    main()

