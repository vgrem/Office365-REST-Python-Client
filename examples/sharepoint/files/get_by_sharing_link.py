"""
Get a file by a sharing link.

Creates an organization link for a file, then resolves the same file from that
guest URL — the reverse of ``share_file``.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/file-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Resolve a file from its sharing link")
    parser.add_argument("--file-url", default="Shared Documents/Financial Sample.xlsx", help="server-relative file URL")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    file = ctx.web.get_file_by_server_relative_url(args.file_url)

    link = file.share_link(SharingLinkKind.OrganizationView).execute_query().value
    resolved = ctx.web.get_file_by_guest_url(str(link)).execute_query()
    print(f"Resolved '{args.file_url}' from its sharing link: {resolved.server_relative_url}")


if __name__ == "__main__":
    main()
