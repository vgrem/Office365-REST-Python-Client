"""
Export the term store hierarchy to CSV (or JSON).

``store.get_all_terms()`` queues a deferred traversal (groups -> sets ->
terms -> children); after ``execute_query()`` the flattened collection can be
serialized with ``write_csv`` (or use ``store.export_tree()`` for the nested tree).

Requires application permission ``TermStore.Read.All``.

https://learn.microsoft.com/en-us/graph/api/termstore-store-list-groups
"""

import argparse

from office365.graph_client import GraphClient
from office365.runtime.converters.csv_writer import write_csv
from tests.settings import client_id, client_secret, root_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Export the term store hierarchy")
    parser.add_argument("--output", default="/tmp/terms_export.csv", help="output CSV file")
    args = parser.parse_args()

    client = (
        GraphClient(tenant=tenant)
        .with_client_secret(client_id, client_secret)
        .require_application_permission("TermStore.Read.All", "TermStore.ReadWrite.All")
    )
    store = client.sites.get_by_url(root_site_url).term_store

    terms = store.get_all_terms().execute_query()
    with open(args.output, "w", newline="") as f:
        write_csv(terms, f)
    print(f"✓ Exported {len(terms)} terms to {args.output}")


if __name__ == "__main__":
    main()
