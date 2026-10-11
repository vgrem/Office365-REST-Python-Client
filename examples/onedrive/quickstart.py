"""
OneDrive in five minutes — the guided tour.

One runnable script that walks the operations you reach for first: connect,
upload a file, list the folder, read the file back, copy it (a *long-running*
action) and clean up. Each step prints what it did; the linked scripts under
``files/`` are the deeper version of any single step, and
``patterns/lro/copy_and_wait.py`` is the deeper version of step 4.

Requires delegated permission ``Files.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/resources/onedrive
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="A guided tour of the most common OneDrive operations")
    parser.add_argument("--keep", action="store_true", help="keep the sample file and folder")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    root = client.me.drive.root

    # 1. Upload a file ----------------------------------------------------
    local = Path(tempfile.gettempdir()) / f"{create_unique_name('quickstart')}.txt"
    local.write_text("Hello from the OneDrive quickstart\n" * 20, encoding="utf-8")
    item = root.upload_file(local).execute_query()
    print(f"1. Uploaded  {item.name}  ({item.size:,} bytes)")

    # 2. List the folder --------------------------------------------------
    children = root.children.get().execute_query()
    print(f"2. Root holds {len(children)} item(s); first: {children[0].name!r}")

    # 3. Read the file back ----------------------------------------------
    back = Path(tempfile.gettempdir()) / f"{create_unique_name('quickstart_dl')}.txt"
    with open(back, "wb") as stream:
        item.download(stream).execute_query()
    print(f"3. Read back {back.stat().st_size:,} bytes")

    # 4. Copy — a long-running operation, awaited -------------------------
    folder = root.create_folder(create_unique_name("quickstart_dst")).execute_query()
    folder = folder.get().execute_query()  # parentReference is required by the copy payload
    result = item.copy(name="quickstart (copy).txt", parent=folder).execute_query()
    copied = result.wait_for_item()
    print(f"4. Copied -> {copied.web_url}")

    # 5. Clean up ---------------------------------------------------------
    if args.keep:
        print(f"5. Kept {item.name!r} and {folder.name!r}.")
        return
    copied.delete_object().execute_query()
    folder.delete_object().execute_query()
    item.delete_object().execute_query()
    local.unlink(missing_ok=True)
    back.unlink(missing_ok=True)
    print("5. Cleaned up.")


if __name__ == "__main__":
    main()
