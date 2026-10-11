"""
Apply a bulk field update to list items with async batches.

Queues one update per matching item — the builders stay synchronous — and then
drains the queue with ``execute_batch_async``. Batches are split exactly like
``execute_batch``, but with ``concurrency`` > 1 they are sent in parallel and
never block the event loop.

Requires ``Sites.FullControl.All`` (writes list items).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-item-operations
"""

from __future__ import annotations

import argparse
import asyncio

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


async def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk-update list items via async $batch")
    parser.add_argument("--list-title", default="Documents", help="list title")
    parser.add_argument("--title-prefix", default="Bulk item", help="only items with this title prefix are updated")
    parser.add_argument("--new-title-suffix", default=" (updated)", help="text appended to each title")
    parser.add_argument("--batch-size", type=int, default=100, help="operations per batch request")
    parser.add_argument("--concurrency", type=int, default=4, help="max concurrent batches (default: 4)")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    items = await ctx.web.lists.get_by_title(args.list_title).items.get().execute_query_async()

    queued = 0
    for item in items:
        title = item.properties.get("Title") or ""
        if title.startswith(args.title_prefix):
            item.set_property("Title", f"{title}{args.new_title_suffix}").update()
            queued += 1

    if queued == 0:
        print(f"No items titled '{args.title_prefix}*' found in '{args.list_title}'.")
        return

    applied = 0

    def on_batch(batch) -> None:
        nonlocal applied
        applied += len(batch)
        print(f"  applied {applied}/{queued}")

    await ctx.execute_batch_async(
        items_per_batch=args.batch_size,
        concurrency=args.concurrency,
        success_callback=on_batch,
    )
    print(f"{applied} of {queued} matching items updated")


asyncio.run(main())
