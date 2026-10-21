"""
Monitor SharePoint Migration API jobs without blocking the event loop.

``GetMigrationJobProgress`` is the recommended status API for an ingestion job,
and ``MigrationServerJob.monitor()`` already polls it — but synchronously, on the
calling thread. ``monitor_async()`` is its awaitable twin: the progress GET and
the wait between polls run on the event loop, so several jobs can be watched at
once and each one's append-only event log is still reduced to a monotonic
``(status, objectsProcessed, total)``.

Watch one or more job ids concurrently (repeat ``--job-id``); each gets its own
cloned context, because a context owns a single request queue. Any ``JobError``
events are printed when a job settles.

Requires an app-only client certificate with the application permission
``Sites.FullControl.All`` (the Migration API does not support delegated auth).

    python monitor_async.py --job-id <job-id>
    python monitor_async.py --job-id <job-a> --job-id <job-b> --interval 30

https://learn.microsoft.com/en-us/sharepoint/dev/apis/migration-api-overview
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from office365.migration import MigrationServerJob
from office365.runtime.operations import Progress
from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


async def watch(ctx: ClientContext, job_id: str, *, interval: float, timeout: float) -> tuple[str, str, list[dict]]:
    """Await one job to a terminal status and return ``(job_id, status, errors)``."""
    job = MigrationServerJob(ctx.site)

    def report(progress: Progress) -> None:
        total = progress.total or "?"
        print(f"  [{job_id}] {progress.stage}: {progress.done}/{total}", flush=True)

    status = await job.monitor_async(job_id, interval=interval, timeout=timeout, progress=report)
    errors = await job.errors_async(job_id)
    return job_id, status, errors


async def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor SharePoint Migration API jobs concurrently")
    parser.add_argument("--job-id", action="append", required=True, help="ingestion job id (repeatable)")
    parser.add_argument("--interval", type=float, default=30, help="seconds between polls (default: 30)")
    parser.add_argument("--timeout", type=float, default=3600, help="per-job timeout in seconds")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    print(f"Watching {len(args.job_id)} job(s): {', '.join(args.job_id)}")

    # One cloned context per job; clones share credentials and the connection pool.
    results = await asyncio.gather(
        *(watch(ctx.clone(site_url), job_id, interval=args.interval, timeout=args.timeout) for job_id in args.job_id),
        return_exceptions=True,
    )

    exit_code = 0
    for result in results:
        if isinstance(result, BaseException):
            print(f"\njob failed to monitor: {result}")
            exit_code = 1
            continue
        job_id, status, errors = result
        print(f"\n[{job_id}] terminal status: {status}")
        for error in errors:
            print(f"  error: {error.get('Message')} ({error.get('ErrorType')})")
        if status.lower() != "succeeded" or errors:
            exit_code = 1
    sys.exit(exit_code)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
