"""
Export a whole Microsoft Graph collection to CSV without loading it all.

``export_to_async(..., page_size=...)`` follows ``@odata.nextLink`` paging one
page at a time and projects/writes each page on the worker pool, so memory stays
flat and the event loop keeps servicing other tasks. A nightly tenant inventory
(users, groups, devices, ...) is the canonical case: the synchronous
``export_to(...).execute_query()`` blocks the loop for the whole run, whereas here
the heartbeat keeps ticking beside it.

    python export_users_async.py --output users.csv --page-size 500

Requires application permission ``User.Read.All``.

https://learn.microsoft.com/en-us/graph/api/user-list
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import sys
import time

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

FIELDS = ["id", "displayName", "userPrincipalName", "mail", "accountEnabled"]


async def heartbeat(stop: asyncio.Event) -> None:
    """Show that the loop stays responsive while the export runs."""
    started = time.monotonic()
    while not stop.is_set():
        print(f"\r  exporting… {time.monotonic() - started:5.1f}s", end="", flush=True)
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(stop.wait(), timeout=1.0)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Stream a Graph collection to CSV asynchronously")
    parser.add_argument("--output", default="users.csv", help="output CSV path")
    parser.add_argument("--page-size", type=int, default=500, help="rows fetched per request")
    args = parser.parse_args()

    client = (
        GraphClient(tenant=tenant)
        .with_client_secret(client_id, client_secret)
        .require_application_permission("User.Read.All")
    )
    async with client:
        # `select` keeps each record small; `page_size` drives nextLink paging.
        users = client.users.select(FIELDS)

        stop = asyncio.Event()
        ticker = asyncio.create_task(heartbeat(stop))
        try:
            # Each page is fetched and appended without blocking the loop; the
            # target is flushed and closed even if the export is cancelled/fails.
            await users.export_to_async(args.output, format="csv", page_size=args.page_size)
        finally:
            stop.set()
            await ticker

    print(f"\nExported users to {args.output}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
