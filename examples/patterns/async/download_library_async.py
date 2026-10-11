"""
Download a whole SharePoint library concurrently (async).

``Folder.download`` is a builder: it enumerates the folder (paged, recursively
by default), preserves the relative tree under the target directory, skips files
that already exist, and — driven with ``await execute_query_async()`` — downloads
with bounded concurrency and per-file retry. No streams, no ``ExitStack``, no
semaphore, no clones: the operation owns all of it. The terminal returns the
operation itself; the outcome is on ``op.value``, and per-file failures land in
``op.value.failures`` instead of aborting the run.

Requires ``Sites.Read.All``.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/file-operations
"""

from __future__ import annotations

import argparse
import asyncio
import tempfile
import time

from office365.runtime.operations import Progress
from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


async def main() -> None:
    parser = argparse.ArgumentParser(description="Download a SharePoint library concurrently")
    parser.add_argument("--list-title", default="Documents", help="document library title")
    parser.add_argument("--output-dir", default="/tmp", help="local output directory (default: temp)")
    parser.add_argument("--concurrency", type=int, default=6, help="max in-flight downloads (default: 6)")
    args = parser.parse_args()

    output_dir = args.output_dir or tempfile.mkdtemp()
    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    root_folder = ctx.web.lists.get_by_title(args.list_title).root_folder

    def report(progress: Progress) -> None:
        if progress.stage == "downloading":
            print(f"[{progress.done}/{progress.total}] downloaded", flush=True)

    op = root_folder.download(output_dir, progress=report)
    started = time.perf_counter()
    await op.execute_query_async(concurrency=args.concurrency)
    elapsed = time.perf_counter() - started

    result = op.value
    print(f"\nDownloaded {result.success}/{result.total} files into {output_dir} ({elapsed:.1f}s)")
    for file, error in result.failures:
        print(f"  failed: {file.server_relative_url}: {error}")


asyncio.run(main())
