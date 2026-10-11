"""
Stream a file's content and verify its hash without buffering the file.

``get_content_stream_async()`` is the primitive behind a resumable download: it
yields the file body in chunks so the bytes can be piped straight to a hash, a
socket or another upload. Here a known payload is uploaded, streamed back in
chunks, and checked against its SHA-256 — with ``on_headers`` capturing the
server's ``Content-Length`` before the first byte, the way a caller decides
whether to page or resume.

Requires delegated permission ``Files.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/driveitem-get-content
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import sys

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.settings import client_id, password, tenant, username

CHUNK_SIZE = 16 * 1024


async def main() -> None:
    parser = argparse.ArgumentParser(description="Stream and hash a OneDrive file")
    parser.add_argument("--keep", action="store_true", help="keep the uploaded file")
    args = parser.parse_args()

    payload = (b"streaming payload line\n" * 4096) + b"tail"
    expected = hashlib.sha256(payload).hexdigest()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    async with client:
        item = await client.me.drive.root.upload(f"{create_unique_name('stream')}.txt", payload).execute_query_async()

        hasher = hashlib.sha256()
        total = 0
        declared = {"length": None}

        def on_headers(headers) -> None:
            declared["length"] = headers.get("Content-Length")

        async for chunk in item.get_content_stream_async(chunk_size=CHUNK_SIZE, on_headers=on_headers):
            hasher.update(chunk)
            total += len(chunk)
            print(f"\r  {total:>10,} bytes", end="", flush=True)

        digest = hasher.hexdigest()
        print(f"\n  declared Content-Length: {declared['length']}")
        print(f"  received: {total:,} bytes")
        print(f"  sha256:   {digest}")
        print(f"  matches:  {digest == expected}")

        if not args.keep:
            await item.delete_object().execute_query_async()
            print("Uploaded file deleted.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
