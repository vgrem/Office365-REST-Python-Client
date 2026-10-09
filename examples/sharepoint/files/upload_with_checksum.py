"""
Upload a file and verify the transfer with a checksum (``upload_with_checksum``).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/file-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Upload a file with a checksum")
    parser.add_argument("--list-title", default="Documents", help="document library title")
    parser.add_argument("--path", default="../../../tests/data/big_buck_bunny.mp4", help="path to the local file")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )

    folder = ctx.web.lists.get_by_title(args.list_title).root_folder
    with open(args.path, "rb") as f:
        file = folder.files.upload_with_checksum(f).execute_query()
    print(f"File has been uploaded into: {file.server_relative_url}")


if __name__ == "__main__":
    main()
