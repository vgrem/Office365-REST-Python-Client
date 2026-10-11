"""
Cancel a long parallel run and resume it without losing queued work.

Runs a tenant-wide site inspection with ``execute_query_parallel_async`` and
cancels it mid-flight — the same effect as pressing Ctrl-C on a long audit or
applying ``asyncio.wait_for``. When a parallel run is interrupted, every query
that had not yet been applied is put back on the context's queue, so a later
call picks the work up again instead of losing it. That at-least-once guarantee
is what makes the async terminal safe to combine with cancellation and timeouts;
a blocking loop would simply stop with the remaining work stranded.

The cancellation is triggered from the progress hook once ``--cancel-after``
sites have completed. Because the interrupted batch is restored as a group, the
resume may re-inspect a few already-seen sites — the point is that none are
silently dropped.

Requires a tenant administrator (the app needs ``Sites.Read.All`` on the admin
site).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/site-operations
"""

from __future__ import annotations

import argparse
import asyncio

from office365.runtime.operations import Progress
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests.settings import admin_site_url, cert_path, cert_thumbprint, client_id, tenant

_MIN_SITES = 2


async def main() -> None:
    parser = argparse.ArgumentParser(description="Cancel and resume a long parallel audit")
    parser.add_argument("--cancel-after", type=int, default=5, help="cancel after N completed sites (default: 5)")
    parser.add_argument("--concurrency", type=int, default=8, help="sites in flight (default: 8)")
    parser.add_argument("--max-sites", type=int, default=200, help="cap the queued sites (default: 200)")
    args = parser.parse_args()

    ctx = ClientContext(admin_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    sites = await Tenant(ctx).get_site_properties_from_sharepoint().execute_query_async()
    urls = [s.url for s in sites if s.url][: args.max_sites]
    if len(urls) < _MIN_SITES:
        print(f"Only {len(urls)} site(s) available; nothing to cancel.")
        return

    # One independent query per site; the parallel terminal drains them together.
    for url in urls:
        Tenant(ctx).get_site_properties_by_url(url)

    completed = 0
    task_ref: asyncio.Task | None = None

    def on_progress(progress: Progress) -> None:
        nonlocal completed, task_ref
        completed = progress.done
        print(f"[{progress.done}/{progress.total}] inspected", flush=True)
        if progress.done >= args.cancel_after and progress.done < progress.total and task_ref is not None:
            print("  -> cancelling", flush=True)
            task_ref.cancel()

    task_ref = asyncio.create_task(ctx.execute_query_parallel_async(concurrency=args.concurrency, progress=on_progress))
    try:
        await task_ref
        print("Completed without cancellation.")
        return
    except asyncio.CancelledError:
        print(f"\nCancelled after {completed} completed site(s).")

    print(f"Queries still pending on the context: {ctx.has_pending_request}")
    print("Resuming the interrupted run...")
    await ctx.execute_query_parallel_async(concurrency=args.concurrency)
    print("Resumed run finished; no queued work was dropped.")


if __name__ == "__main__":
    asyncio.run(main())
