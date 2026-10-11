"""
Incrementally sync a OneDrive drive with a delta token.

The delta feed returns only what changed since a cursor you keep. Persist the
token ``delta_token`` yields after each run, pass it back with ``.token(...)`` next
time, and you have a resumable sync instead of a full re-enumeration. The same
loop works for SharePoint document libraries (``ctx.web.lists[...].delta``).

Requires delegated permission ``Files.Read``.

https://learn.microsoft.com/en-us/graph/api/driveitem-delta
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def load_token(token_path: Path) -> str | None:
    """Read the persisted cursor, if any (a small file, read once up front)."""
    if token_path.exists():
        return token_path.read_text().strip() or None
    return None


def save_token(token_path: Path, token: str) -> None:
    token_path.write_text(token)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Incremental OneDrive sync with delta tokens")
    parser.add_argument("--token-file", default="delta_token.txt", help="where the cursor is kept")
    args = parser.parse_args()
    token_path = Path(args.token_file)
    saved = load_token(token_path)

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    async with client:
        query = client.me.drive.root.delta
        if saved:
            query = query.token(saved)
            print(f"Resuming from the token in {token_path}")
        else:
            print("No saved token; starting a full delta enumeration")

        changes = await query.get_all_async()
        items = list(changes)
        print(f"{len(items)} change(s)")
        for item in items[:10]:
            print(f"  {item.id}  {item.name}")

        token = changes.delta_token
        if token:
            save_token(token_path, token)
            print(f"Saved the new cursor to {token_path}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
