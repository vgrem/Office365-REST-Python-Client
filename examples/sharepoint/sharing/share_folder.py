"""Create an anonymous sharing link for a folder, then resolve it by guest URL.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharing-rest-api
"""

import argparse
import sys

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Share a folder and resolve the guest URL")
    parser.add_argument(
        "--folder-url",
        default="Shared Documents/Archive",
        help="server-relative URL of the folder",
    )
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    folder = ctx.web.get_folder_by_server_relative_url(args.folder_url)
    result = folder.share_link(SharingLinkKind.AnonymousView).execute_query()
    guest_url = result.value.sharingLinkInfo.Url
    if guest_url is None:
        sys.exit("Failed to create a sharing link")
    print(f"Anonymous link: {guest_url}")

    shared_folder = ctx.web.get_folder_by_guest_url(guest_url).execute_query()
    print(f"Resolved folder: {shared_folder.server_relative_url}")


if __name__ == "__main__":
    main()
