"""
Capture a source list's structure (columns, content types, views) as JSON.

Read-only snapshot used to plan a structure-preserving migration: it records the
columns (with ``SchemaXml`` ready for ``CreateFieldAsXml``), content types (with
their ordered field links), and views (with their ordered columns). Nothing is
written to SharePoint.

    python capture_structure.py --list Projects
    python capture_structure.py --all --output ./structure

Each snapshot round-trips through ``ListStructure.to_dict()`` /
``ListStructure.from_dict(...)``. Reprovisioning a snapshot onto a target list is
a separate step (not implemented here).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile

from office365.migration.sharepoint import capture_list_structure
from office365.migration.sharepoint.resolvers import is_migratable_list
from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def _slug(title: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "-" for ch in title).strip("-") or "list"


def main():
    parser = argparse.ArgumentParser(description="Capture a list's structure as JSON")
    parser.add_argument("--list", dest="list_title", default="Documents", help="list/library title (default: Documents)")
    parser.add_argument("--all", action="store_true", help="capture every migratable list/library on the site")
    parser.add_argument("--output", default=None, help="output directory (default: temp dir)")
    args = parser.parse_args()
    if args.output is None:
        args.output = tempfile.gettempdir()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )

    if args.all:
        targets = [entry for entry in ctx.web.lists.get().execute_query() if is_migratable_list(entry)]
    else:
        targets = [ctx.web.lists.get_by_title(args.list_title)]

    os.makedirs(args.output, exist_ok=True)
    for sp_list in targets:
        structure = capture_list_structure(sp_list)
        path = os.path.join(args.output, f"{_slug(structure.title or 'list')}.structure.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(structure.to_dict(), fh, indent=2)
        print(
            f"{structure.title}: {len(structure.fields)} column(s), "
            f"{len(structure.content_types)} content type(s), {len(structure.views)} view(s) -> {path}"
        )


if __name__ == "__main__":
    main()
