"""
Attach custom metadata to files through the library's columns.

A ``DriveItem`` inside a document library also has a backing ``listItem`` whose
``fields`` carry the library's custom columns. Add columns, tag a file, and read
the values back — the pattern behind asset catalogs, classification, retention
tags and any "extra attributes on a file" requirement.

Requires delegated permission ``Sites.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/listitem-update
https://learn.microsoft.com/en-us/graph/api/resources/fieldvalueset
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.onedrive.lists.template_type import ListTemplateType
from tests import create_unique_name
from tests.settings import client_id, client_secret, tenant


def main() -> None:
    parser = argparse.ArgumentParser(description="Tag files with custom metadata in a document library")
    parser.add_argument("--keep", action="store_true", help="keep the library after the demo")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    site = client.sites.root

    # 1. A document library with two custom columns.
    lib = site.lists.add(create_unique_name("Assets"), ListTemplateType.documentLibrary).execute_query()
    lib.columns.add_text("Category").execute_query()
    lib.columns.add_number("RetentionYears").execute_query()
    root = lib.drive.root.get().execute_query()

    # 2. Upload a file and tag it — writes go to listItem/fields.
    item = root.upload("report.txt", b"Quarterly report\n").execute_query()
    fields = item.list_item.fields.get().execute_query()
    fields.set_property("Category", "Finance")
    fields.set_property("RetentionYears", 7)
    fields.update().execute_query()
    print(f"Tagged {item.name!r}: Category=Finance, RetentionYears=7")

    # 3. Read the metadata back on a fresh fetch.
    again = root.get_by_path("report.txt").get().execute_query()
    read_back = again.list_item.fields.get().execute_query()
    print(
        f"  Category={read_back.get_property('Category')!r}  RetentionYears={read_back.get_property('RetentionYears')}"
    )

    if not args.keep:
        lib.delete_object().execute_query()
        print("Library removed.")


if __name__ == "__main__":
    main()
