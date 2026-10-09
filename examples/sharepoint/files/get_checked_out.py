"""
List files that are currently checked out in a document library.

Requires delegated permission ``Sites.Read.All``.

https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-folders-and-files-with-rest
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="List checked-out files in the default document library")
    parser.parse_args()

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    files = ctx.web.default_document_library().get_checked_out_files().execute_query()

    if not files:
        print("No files are checked out.")
        return
    print(f"Checked-out files ({len(files)}):")
    for file in files:
        name = file.properties.get("LeafName") or file.properties.get("Path") or "?"
        print(f"  {name}  (checkedOutById={file.checked_out_by_id})")


if __name__ == "__main__":
    main()
