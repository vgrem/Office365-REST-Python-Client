"""
Gets the files from a folder.
If the 'recursive' flag is set to True, it traverses all sub folders.

The ``progress`` hook fires once per scanned folder — each file is printed as
it is discovered via ``items`` (no separate result loop needed), with a running
counter and size.

See https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/file-operations
"""

import argparse

from office365.runtime.operations import Progress
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from tests.settings import client_id, password, team_site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Gets the files from a folder")
    parser.add_argument("--folder-url", default="Shared Documents", help="server-relative folder URL")
    parser.add_argument("--recursive", action="store_true", help="traverse all sub folders")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )

    counter = {"n": 0}

    def print_files(p: Progress[File]) -> None:
        """Fired per scanned folder — print each file discovered in that folder."""
        for f in p.items or []:
            counter["n"] += 1
            size_kb = (f.length or 0) / 1024
            print(f"  {counter['n']:>4}.  {f.server_relative_url}  ({size_kb:,.0f} KB)")

    root_folder = ctx.web.get_folder_by_server_relative_path(args.folder_url)
    root_folder.get_files(args.recursive, progress=print_files).execute_query()
    print(f"\nListed {counter['n']} files from '{args.folder_url}'")


if __name__ == "__main__":
    main()
