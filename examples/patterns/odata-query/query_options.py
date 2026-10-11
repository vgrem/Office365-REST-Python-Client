"""
OData query parameters — `$select`, `$filter`, `$orderby`, `$top`, `$expand`.

Every collection in the SDK exposes fluent query-option builders. They compose
and shape the eventual request, so you fetch less, filter on the server, and page
predictably — instead of pulling everything and filtering in Python.

Requires delegated permission ``Files.Read``.

https://learn.microsoft.com/en-us/graph/query-parameters
https://learn.microsoft.com/en-us/graph/api/driveitem-list-children
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main() -> None:
    argparse.ArgumentParser(description="Shape drive queries with OData query parameters").parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    root = client.me.drive.root

    # $select + $orderby + $top in one round-trip: ask only for what you render.
    items = (
        root.children.select(["id", "name", "size", "lastModifiedDateTime"])
        .order_by("name")
        .top(5)
        .get()
        .execute_query()
    )
    print(f"First {len(items)} item(s) by name (selected fields only):")
    for item in items:
        print(f"  {item.name:40} {item.size or 0:>12,} bytes")

    # $filter — evaluated by the service, not by you. Use a property the endpoint
    # can filter on. Note that driveItem.size is *not* server-filterable (the
    # SharePoint backing store maps it to SMTotalFileStreamSize), so asking for
    # it raises QueryPropertyNotSupportedError before any request is sent.
    folders = root.children.filter("folder ne null").select(["name", "folder"]).top(10).get().execute_query()
    print(f"\n{len(folders)} folder(s) (filtered server-side)")

    # For a property the service can't filter, narrow the set client-side:
    big = [item for item in root.children.get().execute_query() if (item.size or 0) > 0]
    print(f"{len(big)} item(s) with a non-zero size (filtered client-side)")

    # $expand — pull a related facet in the same call. Note: pairing $expand with a
    # narrow $select on this feed makes Graph stream a malformed body, so expand on
    # its own here.
    with_meta = root.children.expand(["listItem"]).top(1).get().execute_query()
    for item in with_meta:
        print(f"\n{item.name!r} expands to its backing listItem ({item.list_item.id})")

    # The same builders exist on every collection, e.g. users:
    #   client.users.select(["id", "displayName"]).filter("accountEnabled eq true").top(10)


if __name__ == "__main__":
    main()
