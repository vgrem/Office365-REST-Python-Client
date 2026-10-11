"""
Export several usage reports concurrently — a nightly drop in one pass.

``reports.download_report_async()`` streams each CSV through the async transport,
so independent reports overlap instead of running one after another. This is the
practical shape of a scheduled export: gather the standard per-user detail
reports and report the bytes written for each.

The reports download endpoint throttles aggressively (``429`` with a
``Retry-After``), so the script caps concurrency and retries with backoff; a
report that stays throttled is skipped without failing the run. Output goes to
the temp directory by default so nothing lands in the repo.

    python export_usage_async.py
    python export_usage_async.py --period D90 --output-dir /tmp/m365-usage

Requires application permission ``Reports.Read.All``.

https://learn.microsoft.com/en-us/graph/api/resources/report
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.operations import Progress
from tests.settings import client_id, client_secret, tenant

REPORTS = (
    "getEmailActivityUserDetail",
    "getOneDriveActivityUserDetail",
    "getSharePointActivityUserDetail",
    "getTeamsUserActivityUserDetail",
)

_MAX_ATTEMPTS = 3
_HTTP_TOO_MANY_REQUESTS = 429


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _retry_after(exc: ClientRequestException) -> float | None:
    headers = getattr(exc.response, "headers", None) or {}
    value = headers.get("Retry-After")
    try:
        return float(value) if value else None
    except ValueError:
        return None


async def _fetch(
    client: GraphClient, name: str, period: str, out_dir: Path, show_progress: bool, semaphore: asyncio.Semaphore
) -> int:
    def report_progress(progress: Progress) -> None:
        pct = f"{progress.percent:5.1f}%" if progress.total else "  ..."
        print(f"\r  {name}: {pct}", end="", flush=True)

    async with semaphore:
        for attempt in range(1, _MAX_ATTEMPTS + 1):
            try:
                result = await client.reports.download_report_async(
                    name,
                    out_dir / f"{name}.csv",
                    period,
                    progress=report_progress if show_progress else None,
                )
                prefix = "\r" if show_progress else "  "
                print(f"{prefix}  {name}: {result.bytes_written:,} bytes -> {result.file_name}")
                return result.bytes_written
            except ClientRequestException as exc:
                if exc.response.status_code != _HTTP_TOO_MANY_REQUESTS or attempt == _MAX_ATTEMPTS:
                    print(f"  {name}: skipped ({exc.code or exc.response.status_code})")
                    return 0
                delay = _retry_after(exc) or 2**attempt
                print(f"  {name}: throttled, retrying in {delay:.0f}s")
                await asyncio.sleep(delay)
    return 0


async def main() -> None:
    parser = argparse.ArgumentParser(description="Download several usage reports concurrently")
    parser.add_argument("--period", default="D30", help="Aggregation period: D7/D30/D90/D180 (default: D30)")
    parser.add_argument("--max-concurrency", type=int, default=2, help="Reports in flight at once (default: 2)")
    parser.add_argument(
        "--output-dir",
        default=str(Path(tempfile.gettempdir()) / "m365-usage-reports"),
        help="Destination folder (default: a folder in the temp directory)",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    _ensure_dir(out_dir)
    show_progress = sys.stdout.isatty()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    semaphore = asyncio.Semaphore(args.max_concurrency)
    async with client:
        sizes = await asyncio.gather(
            *(_fetch(client, name, args.period, out_dir, show_progress, semaphore) for name in REPORTS)
        )

    written = [size for size in sizes if size]
    print(f"\n{len(written)}/{len(sizes)} report(s), {sum(sizes):,} bytes total in {out_dir}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
