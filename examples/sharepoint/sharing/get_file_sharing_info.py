"""Get all sharing links and permissions for a file.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharing-rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Get sharing information for a file")
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
    info = file.get_sharing_information().execute_query()

    print(f"Anonymous view link: {info.anonymous_view_link}")
    print(f"Anonymous edit link: {info.anonymous_edit_link}")
    print(f"Sharing links ({len(info.sharing_links)}):")
    for link in info.sharing_links:
        print(f"  - {link.Url}  (kind: {link.LinkKind})")
    users = info.shared_with_users_collection
    print(f"Users with access:   {len(users) if users else 0}")


if __name__ == "__main__":
    main()
