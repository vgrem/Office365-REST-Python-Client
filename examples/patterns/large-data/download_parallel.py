"""
Download every file in a folder concurrently.

Enumerates the folder with ``children.get_all()`` (paginated — no 200-item cap)
and queues each file's streamed download, then runs them together with
``execute_query_parallel``. Transient throttling (429/503) is retried per file,
honoring ``Retry-After`` — the bulk-download path for large folders.

Requires delegated permission ``Files.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/driveitem-get-content
"""

import argparse
import os
import tempfile

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.settings import client_id, password, tenant, username

_FILE_COUNT = 6


def main():
    parser = argparse.ArgumentParser(description="Download a folder's files in parallel")
    parser.add_argument("--concurrency", type=int, default=4, help="parallel download streams")
    parser.add_argument("--keep", action="store_true", help="keep the folder after the demo")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    # -- Step 1: create a small folder with files --
    root = client.me.drive.root
    folder = root.create_folder(create_unique_name("parallel")).execute_query()
    for index in range(_FILE_COUNT):
        folder.upload(f"file-{index}.txt", f"{index}\n".encode()).execute_query()
    print(f"Created {_FILE_COUNT} file(s) under '{folder.name}'")

    # -- Step 2: enumerate (paginated) and queue each file's download --
    output_dir = tempfile.mkdtemp(prefix="onedrive-parallel-")
    files = [item for item in folder.children.get_all().execute_query() if item.file is not None]
    for item in files:
        handle = open(os.path.join(output_dir, item.name), "wb")  # noqa: SIM115 — closed by the callback
        item.download_session(handle).after_execute(lambda _r, h=handle: h.close())

    # -- Step 3: run the queued downloads concurrently --
    client.execute_query_parallel(concurrency=args.concurrency)

    print(f"Downloaded {len(files)} file(s) to: {output_dir}")
    if not args.keep:
        folder.delete_object().execute_query()
        print("Folder removed.")


if __name__ == "__main__":
    main()
