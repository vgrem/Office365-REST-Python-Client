"""
Address items in a drive — by path, by id, and through special folders.

The four ways to name a ``DriveItem``. Names are **case-preserving but matched
case-insensitively** (the OneDrive rule); ids are stable, so prefer them for
anything you store.

Requires delegated permission ``Files.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/resources/driveitem
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Address a drive item three ways")
    parser.add_argument("--keep", action="store_true", help="keep the sample file")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    drive = client.me.drive
    root = drive.root

    name = f"{create_unique_name('addressing')}.txt"
    uploaded = root.upload(name, b"address me\n").execute_query()
    print(f"Uploaded {uploaded.name!r} (id={uploaded.id})")

    # 1. by path from the root
    by_path = root.get_by_path(name).get().execute_query()
    print(f"1. by path : {by_path.name!r} -> {by_path.size} bytes")

    # 2. by id (stable across renames — the one to persist)
    by_id = drive.items[uploaded.id].get().execute_query()
    print(f"2. by id   : {by_id.name!r} id={by_id.id}")

    # 3. by enumerating the parent's children (pages automatically)
    children = root.children.get().execute_query()
    match = next(child for child in children if child.name == name)
    print(f"3. children: found {match.name!r} among {len(children)} loaded item(s)")

    # 4. names are case-preserving but matched case-insensitively (OneDrive rule)
    by_case = root.get_by_path(name.upper()).get().execute_query()
    same = by_case.id == uploaded.id
    print(f"4. upper-case path resolves to the same item: {same} (name kept: {by_case.name!r})")

    # Special folders are addressed by canonical name, not by path.
    specials = [folder.name for folder in drive.special.get().execute_query()]
    print(f"   special folders: {', '.join(specials) or '(none)'}")

    if not args.keep:
        uploaded.delete_object().execute_query()
        print("Cleaned up.")


if __name__ == "__main__":
    main()
