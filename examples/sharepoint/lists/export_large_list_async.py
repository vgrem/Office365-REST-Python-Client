"""
Stream a large SharePoint list to JSONL and resume an interrupted export.

Iterates the list with ``async for`` and ``paged(size)`` so only one page is ever
in memory, serializing each item as a JSON line to ``--output`` as it arrives.
On restart the ids already present in the file are skipped, so a run that was
stopped halfway picks up where it left off instead of starting over.

Pair it with a timer to page through lists far larger than memory::

    python examples/sharepoint/lists/export_large_list_async.py --list-title "Orders" --output orders.jsonl

Requires delegated permission ``Sites.Read.All``.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-item-operations
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def load_done_ids(path: str) -> set[str]:
    """Return the ids already present in an existing JSONL export."""
    if not os.path.exists(path):
        return set()
    done: set[str] = set()
    with open(path, encoding="utf-8") as stream:
        for raw in stream:
            line = raw.strip()
            if not line:
                continue
            try:
                done.add(str(json.loads(line)["Id"]))
            except (ValueError, KeyError):
                continue
    return done


async def main() -> None:
    parser = argparse.ArgumentParser(description="Stream a large list to JSONL with resume")
    parser.add_argument("--list-title", default="Documents", help="list title")
    parser.add_argument(
        "--output",
        default=os.path.join(tempfile.gettempdir(), "list-export.jsonl"),
        help="JSONL output file (default: temp dir)",
    )
    parser.add_argument("--page-size", type=int, default=1000, help="items per page (default: 1000)")
    parser.add_argument("--fields", default="", help="comma-separated fields (default: every loaded field)")
    args = parser.parse_args()

    fields = [field.strip() for field in args.fields.split(",") if field.strip()]
    done_ids = load_done_ids(args.output)
    if done_ids:
        print(f"Resuming: {len(done_ids)} item(s) already exported")

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    items = ctx.web.lists.get_by_title(args.list_title).items
    if fields:
        if "Id" not in fields:
            fields.insert(0, "Id")
        items = items.select(fields)
    items = items.paged(args.page_size)

    exported = 0
    with open(args.output, "a", encoding="utf-8") as stream:  # noqa: ASYNC230 - local, brief, off the network
        async for item in items:
            if str(item.id) in done_ids:
                continue
            if fields:
                row = {name: item.get_property(name) for name in fields}
            else:
                row = dict(item.properties)
            stream.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
            exported += 1
            if exported % args.page_size == 0:
                stream.flush()
                print(f"  exported {exported} item(s)", flush=True)

    print(f"Exported {exported} new item(s) to {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
