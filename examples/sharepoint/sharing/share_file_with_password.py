"""Create a password-protected sharing link for a file.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharing-rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from office365.sharepoint.sharing.role_type import RoleType
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Create a password-protected sharing link")
    parser.add_argument(
        "--file-url",
        default="Shared Documents/SharePoint User Guide.docx",
        help="server-relative URL of the file",
    )
    parser.add_argument("--password", default="password", help="password protecting the link")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    target_file = ctx.web.get_file_by_server_relative_url(args.file_url)
    result = target_file.share_link(
        SharingLinkKind.Flexible, role=RoleType.Editor.value, password=args.password
    ).execute_query()
    print(f"Shared link: {result.value.sharingLinkInfo.Url}")


if __name__ == "__main__":
    main()
