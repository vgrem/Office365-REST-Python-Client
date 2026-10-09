"""
Delete or recycle a file from a SharePoint site.

Requires delegated permission ``Sites.Read.All`` (recycle) or ``Sites.FullControl.All`` (permanent delete).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/file-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Delete a file from a SharePoint site")
    parser.add_argument("--file-url", default="Shared Documents/Financial Sample.xlsx", help="server-relative file URL")
    parser.add_argument("--permanent", action="store_true", help="delete permanently instead of recycling")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    file = ctx.web.get_file_by_server_relative_url(args.file_url)

    if args.permanent:
        file.delete_object(ignore_missing=True).execute_query()
        print(f"Deleted: {args.file_url}")
    else:
        recycle_id = file.recycle(ignore_missing=True).execute_query().value
        print(f"Recycled {args.file_url} (recycle bin id {recycle_id})")


if __name__ == "__main__":
    main()
