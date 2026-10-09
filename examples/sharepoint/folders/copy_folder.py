"""
Demonstrates how to copy a folder within a site.

See https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/folder-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, team_site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Copies a folder within a site")
    parser.add_argument("--from-url", default="Shared Documents/Archive/2001", help="source folder url")
    parser.add_argument("--to-url", default="Shared Documents/Archive/2002", help="target folder url")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )

    folder_from = ctx.web.get_folder_by_server_relative_url(args.from_url)
    folder_to = ctx.web.get_folder_by_server_relative_url(args.to_url)

    folder = folder_from.copy_to(folder_to).execute_query()
    print(f"Copied '{folder_from.server_relative_url}' into '{folder.server_relative_url}'")


if __name__ == "__main__":
    main()
