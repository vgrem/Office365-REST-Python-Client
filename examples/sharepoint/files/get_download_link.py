"""
Returns a link for downloading the file without authentication.
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Return a link for downloading a file without authentication")
    parser.add_argument("--file-url", default="Shared Documents/Financial Sample.xlsx", help="server-relative file URL")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )

    # The link stays valid for 1 hour (capped by the web application's max).
    link = (
        ctx.web.get_file_by_server_relative_path(args.file_url)
        .get_pre_authorized_access_url(expiration_hours=1)
        .execute_query()
    )
    print(link.value)


if __name__ == "__main__":
    main()
