"""
Download multiple files in parallel — without managing threads or contexts.

Queue one ``file.download`` per destination, then drain the context's queue with
``execute_query_parallel``: the library overlaps the requests with bounded
concurrency, retries transient failures, and reuses one connection pool.

Requires delegated permission ``Sites.Read.All``.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/file-operations
"""

import argparse
import tempfile
from pathlib import Path

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Download multiple files in parallel")
    parser.add_argument("paths", nargs="+", help="server-relative file paths to download")
    parser.add_argument("--concurrency", type=int, default=4, help="maximum concurrent requests")
    parser.add_argument("--output-dir", default=None, help="local output directory (default: temp)")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    output_dir = Path(args.output_dir or tempfile.mkdtemp())

    handles = []
    for path in args.paths:
        handle = open(output_dir / Path(path).name, "wb")
        handles.append(handle)
        ctx.web.get_file_by_server_relative_path(path).download(handle)  # queue

    try:
        ctx.execute_query_parallel(concurrency=args.concurrency)
    finally:
        for handle in handles:
            handle.close()
    print(f"Downloaded {len(args.paths)} file(s) into {output_dir}")


if __name__ == "__main__":
    main()
