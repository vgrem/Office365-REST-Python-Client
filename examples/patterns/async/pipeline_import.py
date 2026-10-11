"""
Import a local directory into a SharePoint library through a bounded async pipeline.

A producer walks ``--source-dir`` and feeds one ``(remote_name, local_path)`` per
file onto a bounded :class:`asyncio.Queue`; a pool of worker tasks drains it,
reading each file on the executor and uploading it. The bounded queue is the
point: instead of firing one ``asyncio.gather`` over every file (which would
read them all into memory and open an unbounded number of requests), workers
pull only what they can process, so disk reads, HTTP uploads and the event loop
overlap while memory and connection usage stay flat.

Each worker uploads through its own ``ctx.clone(site_url)`` because a context
owns a single pending-query queue; clones share credentials and the connection
pool, so the whole run still uses one token and one set of sockets. Subfolders
are flattened into the file name (``a/b.txt`` -> ``a__b.txt``) so no worker has
to race to create the same remote folder.

Requires delegated permission ``Sites.FullControl.All`` (writes files).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/file-operations
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.lists.templates.type import ListTemplateType
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


async def read_bytes(path: Path) -> bytes:
    """Read a file on the default executor so the I/O never blocks the loop."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, path.read_bytes)


def resolve_source(raw: str) -> Path:
    """Validate and return the source directory (filesystem work off the async path)."""
    source = Path(raw)
    if not source.is_dir():
        raise NotADirectoryError(raw)
    return source


async def worker(
    name: str,
    queue: "asyncio.Queue[tuple[str, Path] | None]",
    ctx: ClientContext,
    list_title: str,
    stats: dict[str, int],
    failures: list[tuple[str, str]],
) -> None:
    """Drain one worker slot: read a file and upload it to the library root."""
    while True:
        item = await queue.get()
        try:
            if item is None:
                return
            remote_name, local_path = item
            content = await read_bytes(local_path)
            clone = ctx.clone(site_url)
            folder = clone.web.lists.get_by_title(list_title).root_folder
            folder.upload_file(remote_name, content)
            await clone.execute_query_async()
            stats["files"] += 1
            stats["bytes"] += len(content)
            print(f"  [{name}] {remote_name} ({len(content):,} bytes)", flush=True)
        except Exception as ex:  # one bad file must not stop the pipeline
            failures.append((str(item[1]) if item else "?", str(ex)))
        finally:
            queue.task_done()


async def produce(queue: "asyncio.Queue[tuple[str, Path] | None]", source: Path) -> None:
    """Walk the source tree and offer each file, blocking when the queue is full."""
    loop = asyncio.get_running_loop()
    files = await loop.run_in_executor(None, lambda: sorted(p for p in source.rglob("*") if p.is_file()))
    for path in files:
        remote_name = path.relative_to(source).as_posix().replace("/", "__")
        await queue.put((remote_name, path))


async def main() -> None:
    parser = argparse.ArgumentParser(description="Import a directory into SharePoint via an async pipeline")
    parser.add_argument("--source-dir", required=True, help="local directory to upload")
    parser.add_argument("--list-title", default="Documents", help="target document library")
    parser.add_argument("--workers", type=int, default=4, help="upload workers (default: 4)")
    parser.add_argument("--queue-size", type=int, default=8, help="bounded queue depth (default: 8)")
    args = parser.parse_args()

    try:
        source = resolve_source(args.source_dir)
    except NotADirectoryError:
        parser.error(f"--source-dir is not a directory: {args.source_dir}")

    worker_count = max(1, args.workers)
    queue: asyncio.Queue[tuple[str, Path] | None] = asyncio.Queue(maxsize=max(worker_count, args.queue_size))
    stats = {"files": 0, "bytes": 0}
    failures: list[tuple[str, str]] = []

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    await ctx.web.ensure_list(args.list_title, template_type=ListTemplateType.DocumentLibrary).execute_query_async()

    started = time.perf_counter()
    workers = [
        asyncio.create_task(worker(f"w{i + 1}", queue, ctx, args.list_title, stats, failures))
        for i in range(worker_count)
    ]
    await produce(queue, source)
    for _ in workers:
        await queue.put(None)
    await asyncio.gather(*workers)
    elapsed = time.perf_counter() - started

    mb = stats["bytes"] / (1024 * 1024)
    throughput = mb / elapsed if elapsed else 0.0
    print(f"\nUploaded {stats['files']} files ({mb:.1f} MB) in {elapsed:.1f}s ({throughput:.1f} MB/s)")
    for path, error in failures:
        print(f"  failed: {path}: {error}")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
