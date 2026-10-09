"""
Upload a small file (up to 4 MB) to a document library.

For larger files use a chunked upload session (see ``upload_large.py``).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/file-operations
"""

import argparse
import os

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Upload a small file to a document library")
    parser.add_argument("--list-title", default="Documents", help="document library title")
    parser.add_argument("--path", default="../../data/Financial Sample.xlsx", help="path to the local file")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    folder = ctx.web.lists.get_by_title(args.list_title).root_folder
    with open(args.path, "rb") as remote_file:
        file = folder.files.upload(remote_file).execute_query()
    print(f"Uploaded {os.path.basename(args.path)} to {file.server_relative_url}")


if __name__ == "__main__":
    main()
