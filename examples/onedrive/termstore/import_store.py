"""
Import a taxonomy hierarchy into a Microsoft Graph term store from JSON.

JSON format mirrors the term store model:
  [group { name, sets: [ set { name, children: [ term { name, children: [] } ] } ] }]

Requires application permission ``TermStore.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/termstore-set-post
"""

import argparse
import json
from pathlib import Path

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, root_site_url, tenant

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "regions.json"


def main():
    parser = argparse.ArgumentParser(description="Import a taxonomy hierarchy from JSON")
    parser.add_argument("--input", default=str(DATA_FILE), help="JSON file to import")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    client = (
        GraphClient(tenant=tenant)
        .with_client_secret(client_id, client_secret)
        .require_application_permission("TermStore.ReadWrite.All")
    )
    store = client.sites.get_by_url(root_site_url).term_store

    store.import_tree(data).execute_query()
    print(f"✓ Imported from {args.input}")


if __name__ == "__main__":
    main()
