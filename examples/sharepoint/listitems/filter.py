"""Filter list items using an OData filter expression.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-item-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Filter list items with an OData expression")
    parser.add_argument("--list-title", default="Documents", help="list title")
    parser.add_argument("--filter", default="FSObjType eq 0", help="OData $filter expression")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    items = ctx.web.lists.get_by_title(args.list_title).items.filter(args.filter).get().execute_query()
    print(f"{len(items)} item(s):")
    for item in items:
        label = item.properties.get("FileLeafRef") or item.properties.get("Title") or "?"
        print(f"  {item.id}: {label}")


if __name__ == "__main__":
    main()
