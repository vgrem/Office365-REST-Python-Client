"""Export a SharePoint list as a package (``.zip``), with per-item progress.

Official documentation: https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-operations
"""

import argparse
import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.exporter import ExportListProgress
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Export a list as a package (.zip)")
    parser.add_argument("--list-title", default="Orders", help="list title")
    parser.add_argument("--output", default=None, help="output zip path (default: temp)")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    lst = ctx.web.lists.get_by_title(args.list_title)
    export_path = args.output or os.path.join(tempfile.mkdtemp(), f"{args.list_title}.zip")

    def print_progress(progress: ExportListProgress) -> None:
        kind = "item" if isinstance(progress.current_item, ListItem) else "file"
        print(f"Exported {kind}: {progress.processed_items}/{progress.total_items}")

    with open(export_path, "wb") as f:
        lst.export(f, True, print_progress).execute_query()
    print(f"Exported '{args.list_title}' to {export_path}")


if __name__ == "__main__":
    main()
