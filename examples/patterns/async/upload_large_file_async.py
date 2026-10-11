"""
Upload a large file to OneDrive with a resumable session, without blocking the loop.

Files above 4 MB cannot use the simple upload: Graph requires an upload session,
which the library drives for you. ``resumable_upload_async()`` creates the session
and PUTs the file in ordered ranges; each chunk is read from disk on the worker
pool and sent through the async transport, so a multi-gigabyte upload never
stalls the event loop. Progress is reported after every accepted chunk.

The chunk size must be a multiple of 320 KiB (2560 bytes); the default (2 MB)
satisfies that. Uploading a large file while continuing to serve requests in the
same event loop is the whole point — the synchronous ``resumable_upload()``
blocks until every range is acknowledged.

Requires delegated permission ``Files.ReadWrite`` (username + password here).

https://learn.microsoft.com/en-us/graph/api/driveitem-createuploadsession
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from office365.graph_client import GraphClient
from office365.runtime.operations import Progress
from tests.settings import client_id, password, tenant, username

CHUNK_SIZE = 320 * 1024 * 5  # 1.6 MB — a multiple of 320 KiB


def report(progress: Progress) -> None:
    if progress.total:
        line = f"\r  {progress.percent:5.1f}%  {progress.done:>12,} / {progress.total:,} bytes"
    else:
        line = f"\r  {progress.done:>12,} bytes"
    print(line, end="", flush=True)


def resolve_source(raw: str) -> Path:
    """Validate the source file (filesystem work off the async path)."""
    source = Path(raw)
    if not source.is_file():
        raise FileNotFoundError(raw)
    return source


async def main() -> None:
    parser = argparse.ArgumentParser(description="Resumable large-file upload to OneDrive")
    parser.add_argument("--source", required=True, help="local file to upload")
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE, help="bytes per chunk (multiple of 320 KiB)")
    args = parser.parse_args()

    source = resolve_source(args.source)

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    async with client:
        uploaded = await client.me.drive.root.resumable_upload_async(
            str(source),
            chunk_size=args.chunk_size,
            progress=report,
        )
        uploaded = await uploaded.get().execute_query_async()
        print(f"\nUploaded '{source.name}' -> {uploaded.web_url}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
