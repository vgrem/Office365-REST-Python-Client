"""
Move a folder under another folder.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/folder-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Move a folder under another folder")
    parser.add_argument("--folder-url", default="Shared Documents/Archive", help="source folder URL")
    parser.add_argument("--target-url", default="Shared Documents/Archive2", help="destination parent folder URL")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    folder_from = ctx.web.get_folder_by_server_relative_url(args.folder_url)
    folder_to_parent = ctx.web.get_folder_by_server_relative_url(args.target_url)

    folder_to = folder_from.move_to(folder_to_parent).execute_query()
    print(f"Moved '{args.folder_url}' into '{folder_to.server_relative_url}'")


if __name__ == "__main__":
    main()
