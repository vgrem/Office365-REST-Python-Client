"""
Bulk-create list items with fleet-wide throttling protection.

Seeds a list with ``--count`` items in parallel batches, but first turns on
opt-in pacing with :meth:`~office365.runtime.client_runtime_context.ClientRuntimeContext.with_rate_limit`.
One shared :class:`~office365.runtime.http.throttling.RateLimiter` then gates
*every* request the context sends as a group: when SharePoint returns a
``Retry-After`` or a high ``X-SharePointHealthScore``, the limiter holds the
whole fleet back instead of hammering the service with the remaining batches.
``execute_batch_async`` still splits and overlaps the batches, and per-query
retry honours ``Retry-After``.

The ``--min-interval`` floor makes the effect visible even against a quiet
tenant: each request waits at least that long after a high health score, so a
run can be slowed deliberately rather than accidentally throttled. See the
synchronous ``examples/sharepoint/throttling`` scripts for the raw header
handling.

Requires ``Sites.FullControl.All`` (creates a list and its items).

https://learn.microsoft.com/en-us/sharepoint/dev/general-development/how-to-avoid-getting-throttled-or-blocked-in-sharepoint-online
"""

from __future__ import annotations

import argparse
import asyncio
import time

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.lists.templates.type import ListTemplateType
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


async def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk-create list items under a shared rate limiter")
    parser.add_argument("--list-title", default="Rate Limited Demo", help="target list (created if missing)")
    parser.add_argument("--count", type=int, default=200, help="items to create (default: 200)")
    parser.add_argument("--title-prefix", default="Item", help="Title prefix for each item")
    parser.add_argument("--batch-size", type=int, default=50, help="operations per batch request")
    parser.add_argument("--concurrency", type=int, default=4, help="max concurrent batches (default: 4)")
    parser.add_argument("--min-interval", type=float, default=0.1, help="pause after a high health score (seconds)")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    target_list = await ctx.web.ensure_list(
        args.list_title, template_type=ListTemplateType.GenericList
    ).execute_query_async()

    # Opt in to pacing before sending the writes. The limiter is shared by every
    # request (and every sub-request of a batch) this context issues.
    ctx.with_rate_limit(health_threshold=80, min_interval=args.min_interval)

    for index in range(args.count):
        target_list.add_item({"Title": f"{args.title_prefix} {index + 1}"})

    started = time.perf_counter()
    await ctx.execute_batch_async(items_per_batch=args.batch_size, concurrency=args.concurrency)
    elapsed = time.perf_counter() - started

    limiter = ctx.rate_limiter
    reason = limiter.last_reason if limiter is not None else None
    paused = f"blocked by '{reason}'" if reason else "not blocked"
    print(f"Created {args.count} items in '{args.list_title}' in {elapsed:.1f}s")
    print(f"Rate limiter: {paused}")


if __name__ == "__main__":
    asyncio.run(main())
