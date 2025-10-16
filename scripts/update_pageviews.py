#!/usr/bin/env python3
"""Fetch GA4 page views and update data/analytics/pageviews.yaml.

Usage:
    python scripts/update_pageviews.py \
        --property-id=123456789 \
        --credentials=/path/to/service-account.json \
        --start-date=2024-01-01 \
        --end-date=today

The script downloads page view counts for each `pagePath` from the specified
GA4 property and writes them into `data/analytics/pageviews.yaml`, which Hugo
consumes to order posts on the home page.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from pathlib import Path
from typing import Dict

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required. Install with `pip install PyYAML`."
    ) from exc

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        OrderBy,
        RunReportRequest,
    )
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit(
        "Google Analytics Data API client is required. Install with "
        "`pip install google-analytics-data`."
    ) from exc

DEFAULT_DATA_PATH = Path("data/analytics/pageviews.yaml")


def parse_args() -> argparse.Namespace:
    today = dt.date.today().isoformat()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--property-id",
        required=True,
        help="GA4 property ID (numbers only, e.g. 123456789)",
    )
    parser.add_argument(
        "--credentials",
        help=(
            "Path to service account JSON credentials. If omitted, the "
            "`GOOGLE_APPLICATION_CREDENTIALS` environment variable will be used."
        ),
    )
    parser.add_argument(
        "--start-date",
        default="2023-01-01",
        help="ISO date for the beginning of the reporting window (default: 2023-01-01)",
    )
    parser.add_argument(
        "--end-date",
        default=today,
        help="ISO date for the end of the reporting window (default: today)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help="Path to the YAML file to update (default: data/analytics/pageviews.yaml)",
    )
    parser.add_argument(
        "--min-views",
        type=int,
        default=0,
        help="Skip pages with fewer total views than this value (default: 0)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10000,
        help="Maximum rows to request from the API (default: 10000)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the aggregated results without writing the YAML file",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Log progress information to stderr",
    )
    return parser.parse_args()


def ensure_credentials(path: str | None) -> None:
    if path:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        raise SystemExit(
            "Google credentials are required. Set --credentials or the "
            "GOOGLE_APPLICATION_CREDENTIALS environment variable."
        )


def fetch_pageviews(
    property_id: str,
    start_date: str,
    end_date: str,
    limit: int,
    verbose: bool = False,
) -> Dict[str, int]:
    client = BetaAnalyticsDataClient()
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews")],
        limit=limit,
        order_bys=[
            OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)
        ],
    )
    response = client.run_report(request)
    results: Dict[str, int] = {}

    for row in response.rows:
        path = row.dimension_values[0].value or ""
        if not path or path.startswith("http"):
            continue
        try:
            views = int(row.metric_values[0].value)
        except (TypeError, ValueError):
            views = 0
        canonical_path = path if path.endswith("/") else f"{path}/"
        results[canonical_path] = views
        if verbose:
            print(f"{canonical_path}: {views}", file=sys.stderr)

    return results


def load_existing(output: Path) -> Dict[str, int]:
    if not output.exists():
        return {}
    with output.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data.get("pageviews", {}) if isinstance(data, dict) else {}


def write_yaml(output: Path, pageviews: Dict[str, int]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"pageviews": dict(sorted(pageviews.items(), key=lambda item: item[0]))}
    with output.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=False)


def main() -> None:
    args = parse_args()
    ensure_credentials(args.credentials)

    if args.verbose:
        print(
            f"Fetching GA4 page views for properties/{args.property_id} "
            f"between {args.start_date} and {args.end_date}…",
            file=sys.stderr,
        )

    fetched = fetch_pageviews(
        property_id=args.property_id,
        start_date=args.start_date,
        end_date=args.end_date,
        limit=args.limit,
        verbose=args.verbose,
    )

    filtered = {k: v for k, v in fetched.items() if v >= args.min_views}
    existing = load_existing(args.output)
    merged = existing | filtered

    if args.dry_run or args.verbose:
        print("\nCollected page views:", file=sys.stderr)
        for path, views in sorted(filtered.items(), key=lambda item: item[1], reverse=True):
            print(f"{views:>8}  {path}", file=sys.stderr)

    if args.dry_run:
        return

    write_yaml(args.output, merged)
    if args.verbose:
        print(f"Updated {args.output} with {len(filtered)} entries.", file=sys.stderr)


if __name__ == "__main__":
    main()
