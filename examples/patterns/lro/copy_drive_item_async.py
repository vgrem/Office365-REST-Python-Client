"""
Copy a OneDrive file and await the server-side copy without blocking the loop.

``driveItem.copy`` is an asynchronous Graph action: it answers ``202 Accepted``
with a monitor URL and finishes later. ``DriveItemCopyResult`` captures that URL
when the query runs; ``wait_for_item_async()`` then polls it off the event loop
(honoring ``Retry-After``) and resolves the newly created item. The progress
hook receives an ``OperationStatus`` snapshot per poll.

Copying a large file while the same event loop keeps serving other requests is
the point: the synchronous ``wait_for_item()`` would freeze the loop until the
copy lands.

Requires delegated permission ``Files.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/driveitem-copy
https://learn.microsoft.com/en-us/graph/long-running-actions-overview
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from office365.graph_client import GraphClient
from office365.runtime.lro import OperationStatus
from tests import create_unique_name
from tests.settings import client_id, password, tenant, username


def report(status: OperationStatus) -> None:
    pct = f"{status.percentage_complete:5.1f}%" if status.percentage_complete is not None else "  ..."
    print(f"\r  {pct}  {status.status or status.http_status}", end="", flush=True)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Copy a drive item and await completion")
    parser.add_argument("--keep", action="store_true", help="keep the samples after the demo")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    async with client:
        root = client.me.drive.root

        # A throwaway source file and destination folder, so the example is safe to re-run.
        source = await root.upload(f"{create_unique_name('lro_src')}.txt", b"source\n").execute_query_async()
        dest = await root.create_folder(create_unique_name("lro_dst")).execute_query_async()
        await dest.get().execute_query_async()  # load parentReference for the copy payload
        print(f"Source: {source.name}")

        # Submit the copy (HTTP 202 + Location) and await the monitor URL.
        result = source.copy(name="copy.txt", parent=dest)
        await result.execute_query_async()
        print(f"  monitor: {result.monitor_url}")

        copied = await result.wait_for_item_async(on_progress=report)
        print(f"\nCopied -> {copied.web_url}")
        print(f"  status={result.last_status.status} resource_id={result.resource_id}")

        if not args.keep:
            await copied.delete_object().execute_query_async()
            await source.delete_object().execute_query_async()
            await dest.delete_object().execute_query_async()
            print("Samples deleted.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
