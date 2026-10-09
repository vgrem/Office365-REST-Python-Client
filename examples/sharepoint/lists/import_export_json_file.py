"""Round-trip a list through a JSON file (export -> import).

Exports a source list to a single JSON array file via ``export_to(..., format="json")``
— the collection's stdlib-only file format — then imports it back into a second
list with ``from_json``. A zero-dependency backup / migration workflow.

Unlike NDJSON (one JSON object per line), the file is one JSON array, so it can
be pretty-printed, diffed, or version-controlled as a unit.
"""

import argparse
import os
import tempfile

from office365.runtime.progress import progress_bar
from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, team_site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Export a list to a JSON file and re-import it")
    parser.add_argument("--source-list", default="Contacts_Large")
    parser.add_argument("--target-list", default="Contacts_Large_Copy")
    parser.add_argument(
        "--select",
        default="Title,FullName,Email,Company,WorkPhone,WorkCity,WorkCountry",
        help="comma-separated fields to export",
    )
    parser.add_argument("--no-progress", action="store_true", help="do not show a tqdm progress bar")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )

    path = os.path.join(tempfile.mkdtemp(), f"{args.source_list}.json")

    # -- Step 1: export list items -> JSON array file --
    source = ctx.web.lists.get_by_title(args.source_list)
    source.items.get_all().select(args.select.split(",")).export_to(path, format="json").execute_query()
    print(f"Exported {args.source_list} -> {path} ({os.path.getsize(path)} bytes)")

    # -- Step 2: import JSON array file -> new list --
    target = ctx.web.lists.ensure_list(args.target_list).execute_query()
    target.ensure_fields(args.select.split(","))
    ctx.execute_query()
    hook = None if args.no_progress else progress_bar(f"Importing into {args.target_list}")
    with open(path, "r", encoding="utf-8") as f:
        target.items.from_json(f, progress=hook).execute_query()
    print(f"Imported {args.source_list} items into '{target.title}'")


if __name__ == "__main__":
    main()
