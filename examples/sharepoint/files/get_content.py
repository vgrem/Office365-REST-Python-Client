"""
Download a small file (< 4 MB) into memory and save it locally.

For larger files use ``download_session`` / ``File.download(path)`` so the body
is streamed without buffering.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/file-operations
"""

import argparse
import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Download file content into memory")
    parser.add_argument("--list-title", default="Site Pages", help="document library title")
    parser.add_argument("--file-name", default="Home.aspx", help="file name")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    file = ctx.web.lists.get_by_title(args.list_title).root_folder.files.get_by_url(args.file_name)
    content = file.get_content().execute_query().value

    local_path = os.path.join(tempfile.mkdtemp(), args.file_name)
    with open(local_path, "wb") as local_file:
        local_file.write(content)
    print(f"[Ok] {len(content):,} bytes saved to {local_path}")


if __name__ == "__main__":
    main()
