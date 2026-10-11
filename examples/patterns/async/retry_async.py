"""
Retry transient failures asynchronously, per query or around a coroutine.

Microsoft 365 throttles with HTTP 429 + ``Retry-After`` and occasionally returns
503; the SDK turns both into retryable errors. ``execute_query_async_retry()``
retries the *pending queries* with exponential backoff (jittered, honoring
``Retry-After``); ``retry_async()`` does the same for any awaitable you supply —
the right tool when each attempt must rebuild its query.

Requires delegated permission ``User.Read`` (username + password here).

https://learn.microsoft.com/en-us/graph/throttling
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


async def main() -> None:
    parser = argparse.ArgumentParser(description="Async retry policies")
    parser.add_argument("--max-retry", type=int, default=5, help="attempts per call")
    args = parser.parse_args()

    def on_failure(attempt: int, ex: Exception) -> None:
        print(f"  attempt {attempt} failed ({type(ex).__name__}); backing off")

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    async with client:
        # 1. Per-query retry: queue the query, then let the context retry it.
        users = client.users.top(5).select(["displayName", "userPrincipalName"])
        users.get()
        await client.execute_query_async_retry(max_retry=args.max_retry, timeout_secs=2, failure_callback=on_failure)
        print(f"users: {len(users)}")

        # 2. Generic retry: each attempt builds a fresh query, so a partially
        #    executed call can't leave stale state behind.
        from office365.runtime.retry import retry_async

        async def fetch_groups():
            groups = client.groups.top(5).select(["displayName"])
            await groups.get().execute_query_async()
            return groups

        groups = await retry_async(fetch_groups, max_retry=args.max_retry, timeout_secs=2, on_failure=on_failure)
        print(f"groups: {len(groups)}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
