"""
Export the top navigation bar structure to a JSON file.

Walks every navigation node (top-level and sub-menus, recursively via
``get_all_nodes``) with a progress bar, then exports the loaded tree through the
collection's ``to_json()`` — the pipeline serialization recurses into each
node's loaded ``Children``.

A Python port of PnP's ``spo-export-topnavbar-including-translations`` script
sample (without the multilingual title resources).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/navigation-api-reference
"""

import argparse
import json
import tempfile
from pathlib import Path

from office365.runtime.progress import progress_bar
from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Export the top navigation bar to JSON")
    parser.add_argument("--site-url", default=site_url, help="site URL")
    parser.add_argument(
        "--output", default=str(Path(tempfile.gettempdir()) / "top_navigation.json"), help="output JSON file"
    )
    parser.add_argument("--no-progress", action="store_true", help="do not show a tqdm progress bar")
    args = parser.parse_args()

    ctx = ClientContext(args.site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )

    hook = None if args.no_progress else progress_bar("Scanning navigation")
    nodes = ctx.web.navigation.top_navigation_bar.get_all_nodes(recursive=True, progress=hook).execute_query()
    if not nodes:
        raise SystemExit("No top navigation nodes found.")

    tree = nodes.to_json()  # recurses through each node's loaded Children
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2)
    print(f"Exported {len(nodes)} navigation node(s) to {args.output}")


if __name__ == "__main__":
    main()
