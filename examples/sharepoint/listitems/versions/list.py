"""
List the version history of list items.

Requires delegated permission ``Sites.Read.All``.

https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, team_site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="List version history for list items")
    parser.add_argument("--list-title", default="Site Pages", help="list to inspect")
    parser.add_argument("--limit", type=int, default=10, help="number of items to inspect")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    items = ctx.web.lists.get_by_title(args.list_title).items.expand(["Versions"]).top(args.limit).get().execute_query()
    for item in items:
        print(f"Item {item.id}: {len(item.versions)} version(s)")
        for version in item.versions:
            print(f"  {version.version_label}  {version.created}")


if __name__ == "__main__":
    main()
