"""
Page through every user in the directory with bounded memory.

``get_all_async(page_size=...)`` follows ``@odata.nextLink`` one page at a time,
projecting only the fields you asked for via ``select`` and reporting progress per
page. This is the shape of a nightly tenant inventory: a directory of hundreds of
thousands of users never has to be materialised in one response, and the event
loop stays free while each page is in flight.

Requires application permission ``User.Read.All``.

https://learn.microsoft.com/en-us/graph/api/user-list
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from office365.graph_client import GraphClient
from office365.runtime.operations import Progress
from tests.settings import client_id, client_secret, tenant

FIELDS = ["id", "displayName", "userPrincipalName", "mail", "accountEnabled"]


def report(progress: Progress) -> None:
    print(f"\r  fetched {progress.done} user(s)", end="", flush=True)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Page through all users with get_all_async")
    parser.add_argument("--page-size", type=int, default=200, help="users per page")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    async with client:
        users = await client.users.select(FIELDS).get_all_async(page_size=args.page_size, progress=report)

    print(f"\n{len(users)} user(s)")
    for user in list(users)[:5]:
        print(f"  {user.display_name:30} {user.user_principal_name}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
