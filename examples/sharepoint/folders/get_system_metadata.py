"""
Retrieve folder authorship metadata (the associated list item's Author/Editor).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/folder-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant

_FIELDS = ["Author/Id", "Author/Title", "Author/Name", "Editor/Id", "Editor/Title", "Editor/Name"]


def main():
    parser = argparse.ArgumentParser(description="Retrieve folder system metadata")
    parser.add_argument("--folder-url", default="Shared Documents/Archive", help="server-relative folder URL")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    item = (
        ctx.web.get_folder_by_server_relative_url(args.folder_url)
        .list_item_all_fields.select(_FIELDS)
        .expand(["Author", "Editor"])
        .get()
        .execute_query()
    )
    print(f"Author: {item.properties.get('Author')}")
    print(f"Editor: {item.properties.get('Editor')}")


if __name__ == "__main__":
    main()
