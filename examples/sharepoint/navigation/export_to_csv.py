"""
Export SharePoint navigation structure to CSV — both Quick Launch
and top nav bars, as a flat inventory.

Walks every node (recursively via ``get_all_nodes``) with a progress bar and
projects the loaded collections to records via ``to_records()`` — the pipeline's
synchronous projection, which is reliable on walked collections (deferred
exporters like ``to_csv`` fire before the recursive walk completes).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/navigation-api-reference
"""

import argparse
import csv
import tempfile
from pathlib import Path

from office365.runtime.progress import progress_bar
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.navigation.nodes.collection import NavigationNodeCollection
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def export_bar(collection: NavigationNodeCollection, writer, no_progress: bool) -> None:
    """Walk a navigation bar and write its nodes as flat rows."""
    hook = None if no_progress else progress_bar("Scanning navigation")
    nodes = collection.get_all_nodes(recursive=True, progress=hook).execute_query()
    for record in nodes.select(["Id", "Title", "Url"]).to_records():
        writer.writerow([record["Title"], record["Url"]])


def main():
    parser = argparse.ArgumentParser(description="Export SharePoint navigation to CSV")
    parser.add_argument("--site-url", default=site_url, help="site URL")
    parser.add_argument("--output", default=str(Path(tempfile.gettempdir()) / "nav_export.csv"), help="output CSV file")
    parser.add_argument("--no-progress", action="store_true", help="do not show tqdm progress bars")
    args = parser.parse_args()

    ctx = ClientContext(args.site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "URL"])
        print("Quick Launch:")
        export_bar(ctx.web.navigation.quick_launch, writer, args.no_progress)
        print("Top nav bar:")
        export_bar(ctx.web.navigation.top_navigation_bar, writer, args.no_progress)

    print(f"Exported to {args.output}")


if __name__ == "__main__":
    main()
