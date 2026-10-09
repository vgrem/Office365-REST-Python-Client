"""
Retrieve a folder's properties.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/folder-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Retrieve a folder's properties")
    parser.add_argument("--folder-url", default="Shared Documents", help="server-relative folder URL")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    folder = ctx.web.get_folder_by_server_relative_url(args.folder_url).get().execute_query()

    print(f"Name:     {folder.name}")
    print(f"URL:      {folder.server_relative_url}")
    print(f"Created:  {folder.time_created}")
    print(f"Modified: {folder.time_last_modified}")


if __name__ == "__main__":
    main()
