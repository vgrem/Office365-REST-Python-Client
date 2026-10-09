"""
Benchmark SharePoint request execution: sequential vs parallel vs batch.

Independent reads (one per list item) are issued three ways and compared by wall
time. It shows how the library overlaps requests on one context
(``execute_query_parallel``) and packs many into a single ``$batch``
(``execute_batch``) — the higher the network latency, the bigger the win.

Requires application permission ``Sites.Read.All``.

https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/batch-processing
"""

from __future__ import annotations

import argparse
import time
from typing import Callable

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def _item_ids(ctx: ClientContext, list_title: str, count: int) -> list[int]:
    """Read up to ``count`` item ids (one page) to use as the workload."""
    items = ctx.web.lists.get_by_title(list_title).items
    loaded = items.select(["Id"]).top(count).get().execute_query()
    ids: list[int] = []
    for item in loaded:
        if item.id is not None:
            ids.append(item.id)
    return ids


def _sequential(ctx: ClientContext, list_title: str, ids: list[int]) -> None:
    items = ctx.web.lists.get_by_title(list_title).items
    for item_id in ids:
        items.get_by_id(item_id).get().execute_query()


def _parallel(ctx: ClientContext, list_title: str, ids: list[int], concurrency: int) -> None:
    items = ctx.web.lists.get_by_title(list_title).items
    for item_id in ids:
        items.get_by_id(item_id).get()
    ctx.execute_query_parallel(concurrency=concurrency)


def _batch(ctx: ClientContext, list_title: str, ids: list[int], batch_size: int, concurrency: int) -> None:
    items = ctx.web.lists.get_by_title(list_title).items
    for item_id in ids:
        items.get_by_id(item_id).get()
    ctx.execute_batch(items_per_batch=batch_size, concurrency=concurrency)


def _timed(action: Callable[[], None]) -> float:
    started = time.monotonic()
    action()
    return (time.monotonic() - started) * 1000


def main():
    parser = argparse.ArgumentParser(description="Benchmark SharePoint execution modes for independent reads")
    parser.add_argument("--list-title", default="Documents", help="list whose items are read")
    parser.add_argument("--count", type=int, default=50, help="number of items to read")
    parser.add_argument("--concurrency", type=int, default=8, help="parallel requests / concurrent batches")
    parser.add_argument("--batch-size", type=int, default=100, help="requests per $batch")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )

    ids = _item_ids(ctx, args.list_title, args.count)
    if not ids:
        print(f"List '{args.list_title}' has no items to read.")
        return

    print(
        f"Reading {len(ids)} item(s) from '{args.list_title}' "
        f"(concurrency={args.concurrency}, batch={args.batch_size})\n"
    )
    timings = {
        "sequential": _timed(lambda: _sequential(ctx, args.list_title, ids)),
        "parallel": _timed(lambda: _parallel(ctx, args.list_title, ids, args.concurrency)),
        "batch": _timed(lambda: _batch(ctx, args.list_title, ids, args.batch_size, args.concurrency)),
    }
    baseline = timings["sequential"] or 1.0
    for mode, elapsed in timings.items():
        print(f"  {mode:12} {elapsed:8.0f} ms   ({baseline / elapsed:.1f}x)")


if __name__ == "__main__":
    main()
