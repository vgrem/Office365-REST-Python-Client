"""List every file in a folder that contains more than 5,000 items.

``Folder.get_files()`` pages through the folder (and, with ``--recursive``, its
subfolders) using ``get_all(page_size=2000)``, so it is **not** throttled by the
5,000-item list view threshold.

For the list-items route, the equivalent is
``lib.items.select(["FileSystemObjectType"]).expand(["File", "Folder"]).get_all()``
(see ``get_all_items.py``).

Official documentation: https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/folder-operations
"""

from __future__ import annotations

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="List all files in a large folder")
    parser.add_argument("--folder-url", default="/Shared Documents", help="server-relative folder url")
    parser.add_argument("--recursive", action="store_true", help="include subfolders")
    parser.add_argument("--page-size", type=int, default=2000, help="items per page (keep <= 5000)")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    folder = ctx.web.get_folder_by_server_relative_url(args.folder_url)

    files = folder.get_files(recursive=args.recursive, page_size=args.page_size).execute_query()

    print(f"Found {len(files)} file(s) in '{args.folder_url}'")
    for file in list(files)[:10]:
        print(f"  {file.name}")


if __name__ == "__main__":
    main()
