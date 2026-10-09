"""Get the sharing links for a folder.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharing-rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Get sharing information for a folder")
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
    info = folder.get_sharing_information().execute_query()

    print(f"Sharing links ({len(info.sharing_links)}):")
    for link in info.sharing_links:
        print(f"  - {link.Url}  (kind: {link.LinkKind})")


if __name__ == "__main__":
    main()
