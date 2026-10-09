"""
Rename a folder.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/folder-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Rename a folder")
    parser.add_argument("--folder-url", default="Shared Documents/Archive", help="server-relative folder URL")
    parser.add_argument("--new-name", default="Archive 2024", help="new folder name")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    folder = ctx.web.get_folder_by_server_relative_url(args.folder_url)
    folder.rename(args.new_name).execute_query()
    print(f"Renamed '{args.folder_url}' to '{args.new_name}'")


if __name__ == "__main__":
    main()
