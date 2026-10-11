"""
Size the worker pool that offloads blocking HTTP calls to async.

With the default ``requests`` transport, every ``await`` runs the blocking send
on a library-owned thread pool — not the event loop's default executor. That pool
is created lazily on the first async request, so tune it *before* that request:
afterwards ``configure_offload_executor()`` raises ``RuntimeError`` (shown here
on purpose). ``execute_query_parallel_async()`` drives the pool: with ``--workers``
smaller than ``--concurrency`` the requests queue for a free worker.

Requires delegated permission ``User.Read`` (username + password here).

https://learn.microsoft.com/en-us/graph/api/user-list
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time

from office365.graph_client import GraphClient
from office365.runtime.operations import Progress
from office365.runtime.transport.offload import configure_offload_executor, shutdown_offload_executor
from tests.settings import client_id, password, tenant, username


async def run_sample(client: GraphClient) -> None:
    """Queue independent reads and let the pool carry the blocking sends."""
    for _ in range(2):
        client.me.get()
        client.users.top(5).select(["displayName"]).get()
        client.groups.top(5).select(["displayName"]).get()

    def report(progress: Progress) -> None:
        print(f"\r  completed {progress.done}/{progress.total}", end="", flush=True)

    started = time.monotonic()
    await client.execute_query_parallel_async(concurrency=6, progress=report)
    print(f"\n  6 queries in {time.monotonic() - started:.2f}s")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Tune the async offload executor")
    parser.add_argument("--workers", type=int, default=8, help="offload pool size")
    parser.add_argument("--concurrency", type=int, default=6, help="in-flight requests")
    args = parser.parse_args()

    # Must happen before the first async request creates the pool.
    configure_offload_executor(max_workers=args.workers, thread_name_prefix="o365-http")

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    try:
        async with client:
            await run_sample(client)

        try:
            configure_offload_executor(max_workers=args.workers)
        except RuntimeError as ex:
            print(f"  reconfiguring after use is rejected: {ex}")
    finally:
        shutdown_offload_executor()
        print("Executor released; the next async request builds a fresh pool.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
