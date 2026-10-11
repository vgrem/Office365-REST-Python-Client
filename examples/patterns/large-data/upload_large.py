"""
Upload a large file using a resumable upload session.

Reads from disk in chunks with progress reporting — the file is never loaded
into memory in full. Best for files larger than a few MB.

For async code, ``resumable_upload_async()`` (see
``examples/patterns/async/upload_large_file_async.py``) does the same without blocking the
event loop.

Requires delegated permission ``Files.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/driveitem-createuploadsession
"""

import argparse
import os

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Upload a large file via a resumable upload session")
    parser.add_argument("--path", required=True, help="path to the local file to upload")
    args = parser.parse_args()

    local_path = args.path
    file_size = os.path.getsize(local_path)
    if file_size == 0:
        parser.error("The file is empty.")

    def print_progress(uploaded_bytes: int) -> None:
        pct = uploaded_bytes / file_size * 100
        print(f"  Uploaded {uploaded_bytes:>12,} / {file_size:,} bytes ({pct:.1f}%)")

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    print(f"Uploading {os.path.basename(local_path)} ({file_size:,} bytes)...")
    uploaded = client.me.drive.root.resumable_upload(local_path, chunk_uploaded=print_progress).execute_query()
    print(f"Uploaded: {uploaded.web_url}")


if __name__ == "__main__":
    main()
