"""
Demonstrates how to upload a large file using chunked upload session.

For async code, ``FileCollection.create_upload_session_async()`` does the same
without blocking the event loop (see ``examples/patterns/async/``).

See https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-folders-and-files-with-rest#working-with-large-files-by-using-rest
"""

import argparse
import os
from typing import Any

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Upload a large file using a chunked upload session")
    parser.add_argument("--path", default="../../../tests/data/big_buck_bunny.mp4", help="path to the local file")
    parser.add_argument("--chunk-size", type=int, default=1_000_000, help="chunk size in bytes")
    parser.add_argument("--target-folder", default="Shared Documents/archive", help="server-relative target folder URL")
    args = parser.parse_args()

    def print_progress(offset: int, *_: Any) -> None:
        file_size = os.path.getsize(args.path)
        pct = offset / file_size * 100
        print(f"Uploaded {offset} bytes / {file_size} bytes ({pct:.1f}%)")

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )

    target_folder = ctx.web.get_folder_by_server_relative_url(args.target_folder)

    with open(args.path, "rb") as f:
        uploaded = target_folder.files.create_upload_session(f, args.chunk_size, print_progress).execute_query()

    print(f"{uploaded.server_relative_url} uploaded")


if __name__ == "__main__":
    main()
