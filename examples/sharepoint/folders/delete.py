"""
Delete or recycle a folder.

Requires delegated permission ``Sites.Read.All`` (recycle) or ``Sites.FullControl.All`` (permanent delete).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/folder-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Delete a folder")
    parser.add_argument("--folder-url", default="Shared Documents/Archive", help="server-relative folder URL")
    parser.add_argument("--permanent", action="store_true", help="delete permanently instead of recycling")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    folder = ctx.web.get_folder_by_server_relative_url(args.folder_url)

    if args.permanent:
        folder.delete_object(ignore_missing=True).execute_query()
        print(f"Deleted: {args.folder_url}")
    else:
        recycle_id = folder.recycle(ignore_missing=True).execute_query().value
        print(f"Recycled {args.folder_url} (recycle bin id {recycle_id})")


if __name__ == "__main__":
    main()
