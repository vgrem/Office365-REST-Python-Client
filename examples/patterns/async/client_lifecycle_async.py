"""
Manage the async client's lifecycle explicitly.

An async client owns a connection pool (the httpx transport when configured) and
must be closed to release it. Prefer the ``async with`` form: ``__aexit__`` awaits
``aclose()`` even when the body raises or is cancelled. When a client outlives a
single scope — a long-lived service object — close it in ``finally`` instead. The
same rule applies to the shared offload executor (see
``tune_offload_executor.py``).

Requires delegated permission ``User.Read`` (username + password here).

https://learn.microsoft.com/en-us/graph/api/user-get
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def build_client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


async def scoped() -> None:
    """The context manager closes the client on every exit path."""
    async with build_client() as client:
        me = await client.me.get().execute_query_async()
        users = await client.users.top(3).select(["displayName", "userPrincipalName"]).get().execute_query_async()
        print(f"scoped: {me.display_name}; sampled {len(users)} user(s)")
    # __aexit__ awaited aclose() — the async transport is released here.


async def long_lived() -> None:
    """A client that outlives one scope is closed in ``finally``."""
    client = build_client()
    try:
        await client.me.get().execute_query_async()
        groups = await client.groups.top(3).select(["displayName"]).get().execute_query_async()
        print(f"long-lived: sampled {len(groups)} group(s)")
    finally:
        await client.aclose()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Async client lifecycle: async with vs explicit aclose")
    parser.parse_args()
    await scoped()
    await long_lived()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
