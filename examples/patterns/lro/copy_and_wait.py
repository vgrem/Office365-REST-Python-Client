"""
Copy a OneDrive file and block until the server-side copy finishes.

``driveItem.copy()`` is a long-running Graph action: the request is accepted with
``202 Accepted`` and a monitor URL, and the copy completes later. The
``DriveItemCopyResult`` returned by ``copy()`` captures that URL when the query
runs; ``wait_for_item()`` then polls it (honoring ``Retry-After``) and returns the
new item. Use this when a synchronous script is fine; see
``examples/patterns/lro/copy_drive_item_async.py`` for the non-blocking twin.

Requires delegated permission ``Files.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/driveitem-copy
https://learn.microsoft.com/en-us/graph/long-running-actions-overview
"""

import argparse

from office365.graph_client import GraphClient
from office365.runtime.lro import OperationStatus
from tests import create_unique_name
from tests.settings import client_id, password, tenant, username


def report(status: OperationStatus) -> None:
    pct = f"{status.percentage_complete:5.1f}%" if status.percentage_complete is not None else "  ..."
    print(f"\r  {pct}  {status.status or status.http_status}", end="", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy a drive item and wait for completion")
    parser.add_argument("--keep", action="store_true", help="keep the samples after the demo")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    root = client.me.drive.root

    source = root.upload(f"{create_unique_name('copy_src')}.txt", b"source\n").execute_query()
    dest = root.create_folder(create_unique_name("copy_dst")).execute_query()
    dest = dest.get().execute_query()  # load parentReference for the copy payload
    print(f"Source: {source.name}")

    result = source.copy(name="copy.txt", parent=dest)
    result.execute_query()
    print(f"  monitor: {result.monitor_url}")

    copied = result.wait_for_item(on_progress=report)
    print(f"\nCopied -> {copied.web_url}")
    print(f"  status={result.last_status.status} resource_id={result.resource_id}")

    if not args.keep:
        copied.delete_object().execute_query()
        source.delete_object().execute_query()
        dest.delete_object().execute_query()
        print("Samples deleted.")


if __name__ == "__main__":
    main()
