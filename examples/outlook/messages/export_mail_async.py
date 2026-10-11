"""
Export a mailbox folder — messages plus attachments — asynchronously.

Walks the folder with ``async for``: each page is awaited while the previous
page is being processed, so a large mailbox never has to be materialized in
memory. For every message it then queues the MIME body and each file attachment
onto the client and drains them with a single
``execute_query_parallel_async(concurrency=...)`` call, so a message with a
dozen attachments downloads them concurrently instead of one after another.

Output layout::

    <output>/<n>-<subject>/message.eml
    <output>/<n>-<subject>/<attachment name>

Requires delegated permission ``Mail.Read``.

https://learn.microsoft.com/en-us/graph/outlook-get-mime-message
"""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from office365.outlook.mail.messages.message import Message
from office365.runtime.client_result import ClientResult
from tests.settings import client_id, password, tenant, username

_UNSAFE = re.compile(r"[^\w.\- ]+")


def safe_name(value: str, fallback: str) -> str:
    """Turn a subject/file name into something safe for a path segment."""
    cleaned = _UNSAFE.sub("_", value).strip().strip(".")
    return cleaned[:80] or fallback


def write_bytes(path: str, content: bytes) -> None:
    """Write a downloaded file on a worker thread (keeps the loop free)."""
    with open(path, "wb") as stream:
        stream.write(content)


async def export_message(
    client: GraphClient,
    message: Message,
    index: int,
    output_dir: str,
    concurrency: int,
    errors: list[str],
) -> None:
    """Fetch one message's MIME body and attachments concurrently, then write them."""
    subject = safe_name(message.subject or "", f"message-{index}")
    target_dir = os.path.join(output_dir, f"{index:04d}-{subject}")
    os.makedirs(target_dir, exist_ok=True)

    downloads: list[tuple[str, ClientResult[bytes]]] = [("message.eml", message.get_content())]
    if message.has_attachments:
        attachments = await message.attachments.get().execute_query_async()
        for position, attachment in enumerate(attachments, start=1):
            name = safe_name(attachment.name or "", f"attachment-{position}")
            downloads.append((name, attachment.get_content()))

    def on_error(_query, error) -> None:
        errors.append(f"{subject}: {error}")

    await client.execute_query_parallel_async(concurrency=concurrency, on_error=on_error)

    loop = asyncio.get_running_loop()
    saved = 0
    for name, result in downloads:
        try:
            await loop.run_in_executor(None, write_bytes, os.path.join(target_dir, name), result.value)
            saved += 1
        except (AssertionError, TypeError, OSError):
            # Non-file (item/reference) attachments have no $value to download.
            errors.append(f"{subject}: {name} has no downloadable content")
    print(f"[{index}] {subject}: saved {saved}/{len(downloads)} file(s)", flush=True)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Export messages and attachments asynchronously")
    parser.add_argument("--folder", default="inbox", help="mail folder name or id")
    parser.add_argument("--output", default=str(Path(tempfile.gettempdir()) / "mail-export"), help="output directory")
    parser.add_argument("--limit", type=int, default=0, help="max messages to export (0 = all)")
    parser.add_argument("--page-size", type=int, default=25, help="messages per page (default: 25)")
    parser.add_argument("--concurrency", type=int, default=4, help="concurrent downloads (default: 4)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    os.makedirs(args.output, exist_ok=True)

    messages = (
        client.me.mail_folders[args.folder]
        .messages.select(["id", "subject", "receivedDateTime", "hasAttachments"])
        .paged(args.page_size)
    )

    exported = 0
    errors: list[str] = []
    async for message in messages:
        if args.limit and exported >= args.limit:
            break
        exported += 1
        await export_message(client, message, exported, args.output, args.concurrency, errors)

    print(f"\nExported {exported} message(s) to {args.output}")
    for error in errors:
        print(f"  skipped: {error}")


if __name__ == "__main__":
    asyncio.run(main())
