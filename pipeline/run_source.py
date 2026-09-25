"""CLI: python -m pipeline.run_source <source_name> [--start YYYY-MM-DD] [--days 7]."""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import date

from pipeline.runner import run_source
from pipeline.sources.registry import SOURCES


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run one source scraper over a date window and upsert events."
    )
    parser.add_argument(
        "source",
        choices=[s.name for s in SOURCES],
        help="Source name from pipeline.sources.registry.",
    )
    parser.add_argument(
        "--start",
        type=date.fromisoformat,
        default=date.today(),
        help="First day to scrape (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="How many consecutive days to scrape (default 7).",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable debug logging."
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    summary = run_source(args.source, start=args.start, days=args.days)
    print(
        f"[{summary.source_name}] {summary.days} day(s) from {args.start}: "
        f"parsed={summary.parsed} inserted={summary.inserted} "
        f"updated={summary.updated} empty_days={summary.empty_days}"
    )
    if summary.errors:
        print("Errors:")
        for e in summary.errors:
            print(f"  - {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
