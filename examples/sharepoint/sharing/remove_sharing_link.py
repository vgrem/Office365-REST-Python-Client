"""Create an anonymous sharing link, then remove it.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharing-rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant

LINK_KINDS = {"view": SharingLinkKind.AnonymousView, "edit": SharingLinkKind.AnonymousEdit}


def main():
    parser = argparse.ArgumentParser(description="Create and remove a sharing link")
    parser.add_argument(
        "--file-url",
        default="Shared Documents/Financial Sample.xlsx",
        help="server-relative URL of the file",
    )
    parser.add_argument("--kind", choices=sorted(LINK_KINDS), default="view", help="anonymous link kind")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    file = ctx.web.get_file_by_server_relative_url(args.file_url)
    kind = LINK_KINDS[args.kind]

    link_url = file.share_link(kind).execute_query().value.sharingLinkInfo.Url
    print(f"Created: {link_url}")

    file.unshare_link(kind).execute_query()
    print(f"Removed anonymous {args.kind} link")


if __name__ == "__main__":
    main()
