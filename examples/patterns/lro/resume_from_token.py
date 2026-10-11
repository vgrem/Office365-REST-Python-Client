"""
Resume a long-running copy from a continuation token.

An operation's monitor URL is the only state needed to keep polling it. A
``ContinuationToken`` serializes that URL (with its resolution mode) to JSON, so
a job can be picked up by a later call, process or host — the pattern behind
durable copy/migration workers. This example submits a copy, persists the token,
then deliberately throws the in-memory result away and resumes from the token
alone, exactly as a restarted worker would.

Requires delegated permission ``Files.ReadWrite``.

https://learn.microsoft.com/en-us/graph/long-running-actions-overview
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from office365.graph_client import GraphClient
from office365.runtime.lro import ContinuationToken, OperationPoller, OperationStatus
from tests import create_unique_name
from tests.settings import client_id, password, tenant, username


def report(status: OperationStatus) -> None:
    pct = f"{status.percentage_complete:5.1f}%" if status.percentage_complete is not None else "  ..."
    print(f"\r  {pct}  {status.status or status.http_status}", end="", flush=True)


def write_token(token_path: Path, token: str) -> None:
    token_path.write_text(token)


def read_token(token_path: Path) -> str:
    return token_path.read_text()


def remove_token(token_path: Path) -> None:
    token_path.unlink(missing_ok=True)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Resume a long-running operation from a token")
    parser.add_argument("--token-file", default="lro_continuation.json", help="where to persist the token")
    parser.add_argument("--keep", action="store_true", help="keep the sample files")
    args = parser.parse_args()
    token_path = Path(args.token_file)

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    async with client:
        root = client.me.drive.root
        source = await root.upload(f"{create_unique_name('resume_src')}.txt", b"resume\n").execute_query_async()
        dest = await root.create_folder(create_unique_name("resume_dst")).execute_query_async()
        await dest.get().execute_query_async()

        # -- "Process 1": submit and persist the continuation token, then drop it --
        result = source.copy(name="copy.txt", parent=dest)
        await result.execute_query_async()
        poller = result.to_poller(interval=2, timeout=300)
        write_token(token_path, poller.to_continuation_token().to_json())
        print(f"Submitted copy; token written to {token_path}")

    # -- "Process 2": resume from the token alone, with a fresh client --
    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    async with client:
        token = ContinuationToken.from_json(read_token(token_path))
        print(f"Resumed at status={token.status!r}; polling {token.poll_url}")
        poller = OperationPoller.from_continuation_token(client, token, interval=2, timeout=300, authenticate=True)
        status = await poller.wait_async(on_progress=report)
        print(f"\nTerminal: {status.status} (resource_id={status.resource_id})")

        if status.resource_id and not args.keep:
            copied = await client.me.drive.items[status.resource_id].get().execute_query_async()
            await copied.delete_object().execute_query_async()
        if not args.keep:
            source = await client.me.drive.root.get_by_path(source.name).get().execute_query_async()
            await source.delete_object().execute_query_async()
            dest = await client.me.drive.root.get_by_path(dest.name).get().execute_query_async()
            await dest.delete_object().execute_query_async()
            remove_token(token_path)
            print("Samples cleaned up.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
