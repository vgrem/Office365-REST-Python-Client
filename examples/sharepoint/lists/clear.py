"""Delete all items in a list.

Official documentation: https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Delete all items in a list")
    parser.add_argument("--list-title", default="Company Tasks", help="list title")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    target_list = ctx.web.lists.get_by_title(args.list_title)
    target_list.clear().execute_batch()
    print(f"Cleared '{args.list_title}' ({target_list.item_count} item(s) remaining)")


if __name__ == "__main__":
    main()
