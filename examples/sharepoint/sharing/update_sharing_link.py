"""Create a sharing link, then update its expiration date.

The second call targets the link created by the first one (via its share id),
so the expiration is updated in place instead of creating a second link.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharing-rest-api
"""

import argparse
import sys
from datetime import datetime, timedelta, timezone

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Create then update a sharing link's expiration")
    parser.add_argument(
        "--file-url",
        default="Shared Documents/Financial Sample.xlsx",
        help="server-relative URL of the file",
    )
    parser.add_argument("--initial-days", type=int, default=7, help="initial expiry in days")
    parser.add_argument("--updated-days", type=int, default=30, help="updated expiry in days")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    file = ctx.web.get_file_by_server_relative_url(args.file_url)

    expires = datetime.now(timezone.utc) + timedelta(days=args.initial_days)
    link = file.share_link(SharingLinkKind.AnonymousView, expiration=expires).execute_query().value.sharingLinkInfo
    if link.ShareId is None:
        sys.exit("The server did not return a share id for the created link")
    print(f"Created link (expires in {args.initial_days} days): {link.Url}")

    expires = datetime.now(timezone.utc) + timedelta(days=args.updated_days)
    updated = (
        file.share_link(SharingLinkKind.AnonymousView, expiration=expires, share_id=link.ShareId)
        .execute_query()
        .value.sharingLinkInfo
    )
    print(f"Updated link (expires in {args.updated_days} days): {updated.Url}")


if __name__ == "__main__":
    main()
