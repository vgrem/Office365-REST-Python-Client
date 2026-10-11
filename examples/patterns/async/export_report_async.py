"""
Stream a usage report to disk asynchronously, showing the loop stays free.

``reports.download_report_async()`` follows the report's pre-authenticated
download URL through the configured async transport and writes the CSV in
chunks — the report is never buffered in memory and the event loop is never
blocked. That matters for `*UserDetail` reports, which can be tens of megabytes:
a heartbeat keeps ticking beside the download to prove it.

Requires application permission ``Reports.Read.All``.

https://learn.microsoft.com/en-us/graph/api/reportroot-getteamsuseractivityuserdetail
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import sys
import time

from office365.graph_client import GraphClient
from office365.runtime.operations import Progress
from tests.settings import client_id, client_secret, tenant


async def heartbeat(stop: asyncio.Event) -> None:
    started = time.monotonic()
    while not stop.is_set():
        print(f"\r  streaming… {time.monotonic() - started:5.1f}s", end="", flush=True)
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(stop.wait(), timeout=1.0)


def report_progress(progress: Progress) -> None:
    pct = f"{progress.percent:5.1f}%" if progress.total else "  ..."
    print(f"\r  {pct}  {progress.done:>12,} bytes", end="", flush=True)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Stream a Graph usage report to CSV asynchronously")
    parser.add_argument("--report", default="getTeamsUserActivityUserDetail", help="Graph report function name")
    parser.add_argument("--period", default="D30", help="D7/D30/D90/D180 (UserDetail reports)")
    parser.add_argument("--output", default="report.csv", help="output CSV path")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    async with client:
        stop = asyncio.Event()
        ticker = asyncio.create_task(heartbeat(stop))
        try:
            result = await client.reports.download_report_async(
                args.report, args.output, args.period, progress=report_progress
            )
        finally:
            stop.set()
            await ticker

    print(f"\nWrote {result.bytes_written:,} bytes to {args.output} ({result.file_name})")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
