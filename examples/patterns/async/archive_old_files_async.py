"""
Archive files older than a retention window, then delete the originals.

A real retention job is more than a copy: it decides *which* files are old
enough, copies each one (a Graph long-running operation), verifies the copy
landed, and only then deletes the source. Getting the order wrong loses data.

This example walks a OneDrive folder, selects files older than ``--days``, and
runs the decision → copy → verify → delete workflow with bounded concurrency.
It is a **dry run by default**: it prints the plan and touches nothing until you
pass ``--apply``. The copies poll off the event loop, so the batch of copies
overlaps instead of completing one at a time; queue-based calls (submit,
verify, delete) are serialized because a context owns a single request queue,
while the polling itself is safe to run concurrently.

With no folders it generates a sample source folder and archive folder, so the
example is self-contained:

    python archive_old_files_async.py                    # plan only
    python archive_old_files_async.py --apply            # copy + verify + delete
    python archive_old_files_async.py --source-folder Reports --archive-folder Archive --days 180 --apply

Requires delegated permission ``Files.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/driveitem-copy
https://learn.microsoft.com/en-us/graph/api/driveitem-delete
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.onedrive.driveitems.driveItem import DriveItem
from office365.runtime.lro import OperationStatus
from tests import create_unique_name
from tests.settings import client_id, password, tenant, username

_SAMPLE_COUNT = 3


def is_older_than(item: DriveItem, cutoff: datetime) -> bool:
    """Whether the item was last modified before ``cutoff`` (treating naive stamps as UTC)."""
    modified = item.last_modified_date_time
    if modified.tzinfo is None:
        modified = modified.replace(tzinfo=timezone.utc)
    return modified < cutoff


def report(status: OperationStatus) -> None:
    pct = f"{status.percentage_complete:5.1f}%" if status.percentage_complete is not None else "  ..."
    print(f"  copy   {pct} {status.status or status.http_status}", flush=True)


async def bootstrap(client: GraphClient) -> tuple[DriveItem, DriveItem]:
    """Create a sample source folder with files and an archive folder."""
    root = client.me.drive.root
    source = await root.create_folder(create_unique_name("archive_src")).execute_query_async()
    archive = await root.create_folder(create_unique_name("archive_dst")).execute_query_async()
    for index in range(1, _SAMPLE_COUNT + 1):
        await source.upload(f"retained-{index}.txt", f"sample {index}\n".encode()).execute_query_async()
    return source, archive


async def list_candidates(folder: DriveItem, cutoff: datetime, lock: asyncio.Lock) -> list[DriveItem]:
    """List the files in ``folder`` that are older than ``cutoff``."""
    async with lock:  # a context owns one request queue — serialize queue-based calls
        children = await folder.children.get().execute_query_async()
    return [item for item in children if item.is_file and is_older_than(item, cutoff)]


async def archive_one(
    client: GraphClient,
    item: DriveItem,
    archive: DriveItem,
    *,
    sem: asyncio.Semaphore,
    lock: asyncio.Lock,
    interval: float,
    timeout: float,
    apply: bool,
) -> bool:
    """Copy one file to the archive, verify it, then (with ``--apply``) delete the original."""
    async with sem:
        if not apply:
            print(f"  plan   {item.name} (modified {item.last_modified_date_time:%Y-%m-%d})")
            return True
        try:
            async with lock:
                result = item.copy(name=item.name, parent=archive)
                await result.execute_query_async()
            status = await result.to_poller(interval=interval, timeout=timeout).wait_async(on_progress=report)
            if status.resource_id is None:
                raise RuntimeError("copy completed without a resource id")
            async with lock:
                copied = await client.me.drive.items[status.resource_id].get().execute_query_async()
            if copied.size != item.size:
                raise RuntimeError(f"size mismatch (source={item.size}, copy={copied.size})")
            async with lock:
                await item.delete_object().execute_query_async()
        except Exception as ex:  # noqa: BLE001 — isolate per-file failures, never delete on failure
            print(f"  fail   {item.name}: {ex}")
            return False
        print(f"  done   {item.name} -> archive ({item.size} bytes)")
        return True


async def main() -> None:
    parser = argparse.ArgumentParser(description="Archive files older than a retention window")
    parser.add_argument("--source-folder", help="folder to scan (samples are generated when omitted)")
    parser.add_argument("--archive-folder", help="folder to copy expired files into")
    parser.add_argument("--days", type=int, default=0, help="minimum age in days (0 = any age)")
    parser.add_argument("--apply", action="store_true", help="copy and delete; without it, plan only")
    parser.add_argument("--concurrency", type=int, default=4, help="copies in flight (default: 4)")
    parser.add_argument("--interval", type=float, default=5, help="seconds between polls (default: 5)")
    parser.add_argument("--timeout", type=float, default=1800, help="per-copy timeout in seconds")
    parser.add_argument("--keep", action="store_true", help="keep the generated samples after --apply")
    args = parser.parse_args()

    if bool(args.source_folder) != bool(args.archive_folder):
        parser.error("pass both --source-folder and --archive-folder, or neither (samples are generated)")

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    async with client:
        root = client.me.drive.root
        bootstrapped = False
        if args.source_folder:
            source = await root.get_by_path(args.source_folder).get().execute_query_async()
            archive = await root.get_by_path(args.archive_folder).get().execute_query_async()
        else:
            source, archive = await bootstrap(client)
            bootstrapped = True
            print(f"Generated samples in {source.name}; archive is {archive.name}")

        lock = asyncio.Lock()
        cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
        candidates = await list_candidates(source, cutoff, lock)
        print(f"{len(candidates)} file(s) in {source.name} older than {args.days} day(s)")
        if not candidates:
            print("Nothing to do — lower --days (0 archives everything) or point at another folder.")
        else:
            mode = "archive" if args.apply else "dry-run (pass --apply to copy and delete)"
            print(f"Mode: {mode}")
            sem = asyncio.Semaphore(args.concurrency)
            outcomes = await asyncio.gather(
                *(
                    archive_one(
                        client,
                        item,
                        archive,
                        sem=sem,
                        lock=lock,
                        interval=args.interval,
                        timeout=args.timeout,
                        apply=args.apply,
                    )
                    for item in candidates
                )
            )
            done = sum(1 for ok in outcomes if ok)
            if args.apply:
                print(f"\nArchived {done}/{len(candidates)} file(s)")
            else:
                print(f"\n{len(candidates)} file(s) would be archived (dry run)")

        if bootstrapped and args.apply and not args.keep:
            await source.delete_object().execute_query_async()
            await archive.delete_object().execute_query_async()
            print("Sample folders removed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
