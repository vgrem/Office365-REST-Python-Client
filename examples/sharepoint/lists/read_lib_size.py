"""Retrieve a document library's storage size (root folder storage metrics).

Official documentation: https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Retrieve a document library's storage size")
    parser.add_argument("--list-title", default="Documents", help="document library title")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    lib = ctx.web.lists.get_by_title(args.list_title).expand(["RootFolder/StorageMetrics"]).get().execute_query()
    print(f"Total size (bytes): {lib.root_folder.storage_metrics.total_size:,}")
    print(f"Item count:         {lib.item_count:,}")


if __name__ == "__main__":
    main()
