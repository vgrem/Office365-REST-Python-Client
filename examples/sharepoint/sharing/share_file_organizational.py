"""Create an organization-wide (authenticated) view link for a file.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharing-rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Create an organization sharing link for a file")
    parser.add_argument(
        "--file-url",
        default="Shared Documents/Financial Sample.xlsx",
        help="server-relative URL of the file",
    )
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    file = ctx.web.get_file_by_server_relative_url(args.file_url)
    result = file.share_link(SharingLinkKind.OrganizationView).execute_query()
    print(f"Organization link: {result.value.sharingLinkInfo.Url}")


if __name__ == "__main__":
    main()
