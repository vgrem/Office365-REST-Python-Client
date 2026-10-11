"""
Export list items to a CSV file.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-item-operations
"""

import argparse
import tempfile
from pathlib import Path

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Export list items to CSV")
    parser.add_argument("--list-title", default="Documents", help="list title")
    parser.add_argument("--output", default=str(Path(tempfile.gettempdir()) / "list_items.csv"), help="output CSV file")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    with open(args.output, "w", newline="") as f:
        ctx.web.lists.get_by_title(args.list_title).items.select(["Title", "Created"]).to_csv(f).execute_query()
    print(f"Exported to {args.output}")


if __name__ == "__main__":
    main()
