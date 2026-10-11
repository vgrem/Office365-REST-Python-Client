"""
Upload a large file to SharePoint with a chunked session, asynchronously.

``FileCollection.create_upload_session_async()`` is an awaitable that creates the
file, uploads every chunk through the configured async transport, and commits the
last fragment before it returns — so a multi-gigabyte upload never blocks the
event loop and ``execute_query()`` is not needed. The ``progress`` hook receives
the bytes committed so far.

Requires delegated permission ``Sites.ReadWrite.All``.

https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-folders-and-files-with-rest#working-with-large-files-by-using-rest
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from office365.runtime.operations import Progress
from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def report(progress: Progress) -> None:
    if progress.total:
        print(f"\r  {progress.percent:5.1f}%  {progress.done:>12,}/{progress.total:,} bytes", end="", flush=True)
    else:
        print(f"\r  {progress.done:>12,} bytes", end="", flush=True)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Async chunked upload to SharePoint")
    parser.add_argument("--path", required=True, help="local file to upload")
    parser.add_argument("--target-folder", default="Shared Documents", help="server-relative folder URL")
    parser.add_argument("--chunk-size", type=int, default=1_000_000, help="bytes per chunk")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    try:
        target = ctx.web.get_folder_by_server_relative_url(args.target_folder)
        uploaded = await target.files.create_upload_session_async(args.path, args.chunk_size, progress=report)
        print(f"\nUploaded -> {uploaded.server_relative_url}")
    finally:
        await ctx.aclose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
