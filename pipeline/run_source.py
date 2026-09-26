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
        default=None,
        help="First day to scrape (YYYY-MM-DD). Defaults to today − --lookback.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="How many consecutive days from --start (default 7).",
    )
    parser.add_argument(
        "--lookback",
        type=int,
        default=0,
        help=(
            "Number of days BEFORE today to also load. Shifts --start earlier "
            "and extends --days by the same amount. Ex: --lookback 3 --days 7 "
            "with default start = J−3 → J+7 (11 days total)."
        ),
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable debug logging."
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    from datetime import timedelta as _td
    start = args.start if args.start is not None else date.today() - _td(days=args.lookback)
    total_days = args.days + (args.lookback if args.start is None else 0)
    summary = run_source(args.source, start=start, days=total_days)
    print(
        f"[{summary.source_name}] {summary.days} day(s) from {start}: "
        f"parsed={summary.parsed} inserted={summary.inserted} "
        f"updated={summary.updated} merged={summary.merged} "
        f"skipped={summary.skipped} empty_days={summary.empty_days}"
    )
    if summary.errors:
        print("Errors:")
        for e in summary.errors:
            print(f"  - {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
