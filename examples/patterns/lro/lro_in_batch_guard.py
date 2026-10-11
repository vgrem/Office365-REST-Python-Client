"""
Catch a long-running operation that was submitted inside a batch.

Batching is for many short, independent requests. A long-running operation — a
drive-item copy, for instance — answers ``202 Accepted`` with a monitor URL that
must be captured so the operation can be awaited. A batch envelope does *not*
route that URL back to the operation's result, so a batched copy yields a
``DriveItemCopyResult`` whose ``monitor_url`` is empty: the copy runs, but nothing
waits for it. This example shows a small guard that detects a
``LongRunningOperationResult`` among a batch's return types and fails loudly, then
does it the right way — submit the LRO on its own and await it.

Requires delegated permission ``Files.ReadWrite``.

https://learn.microsoft.com/en-us/graph/long-running-actions-overview
https://learn.microsoft.com/en-us/graph/json-batching
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from typing import Any, Iterable

from office365.graph_client import GraphClient
from office365.runtime.lro import LongRunningOperationResult, OperationStatus
from tests import create_unique_name
from tests.settings import client_id, password, tenant, username


class BatchedLongRunningOperationError(RuntimeError):
    """Raised when a long-running operation was submitted inside a batch."""


def report(status: OperationStatus) -> None:
    pct = f"{status.percentage_complete:5.1f}%" if status.percentage_complete is not None else "  ..."
    print(f"\r  {pct}  {status.status or status.http_status}", end="", flush=True)


async def guarded_batch(client: GraphClient, **kwargs: Any) -> None:
    """Run pending queries as a batch, refusing ones that can no longer be awaited.

    ``success_callback`` receives each batch's return types; any
    ``LongRunningOperationResult`` in that list was batched and lost its monitor
    URL, so raise instead of letting the caller poll nothing.
    """
    offenders: list[LongRunningOperationResult] = []

    def scan(return_types: Iterable[Any] | None) -> None:
        offenders.extend(rt for rt in (return_types or ()) if isinstance(rt, LongRunningOperationResult))

    await client.execute_batch_async(success_callback=scan, **kwargs)
    if offenders:
        raise BatchedLongRunningOperationError(
            f"{len(offenders)} long-running operation(s) were batched; the batch "
            "envelope drops their monitor URLs. Submit LROs individually and await them."
        )


async def main() -> None:
    parser = argparse.ArgumentParser(description="Detect a long-running operation batched by mistake")
    parser.add_argument("--keep", action="store_true", help="keep the sample files")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    async with client:
        root = client.me.drive.root
        source = await root.upload(f"{create_unique_name('guard_src')}.txt", b"source\n").execute_query_async()
        dest = await root.create_folder(create_unique_name("guard_dst")).execute_query_async()
        await dest.get().execute_query_async()

        print("Batching a copy with ordinary work (the mistake)...")
        try:
            source.copy(name="batched.txt", parent=dest)
            await guarded_batch(client, items_per_batch=20)
            print("  (no batched LRO detected)")
        except BatchedLongRunningOperationError as ex:
            print(f"  guard raised: {ex}")
        except Exception as ex:
            print(f"  batch rejected the LRO: {type(ex).__name__}: {ex}")

        print("Correct pattern: submit the copy on its own and await the monitor URL.")
        result = source.copy(name="separate.txt", parent=dest)
        await result.execute_query_async()
        copied = await result.wait_for_item_async(on_progress=report)
        print(f"\n  copied -> {copied.web_url}")

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
