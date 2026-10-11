"""
Records management — list the retention labels defined in the tenant.

A quick inventory: every label, its retention trigger and end action, and
whether it is currently applied to any content.

    python list_labels.py
    python list_labels.py --in-use

Requires delegated permission ``RecordsManagement.Read.All`` **and** the
Compliance Administrator (or Global Administrator) role.

https://learn.microsoft.com/en-us/graph/api/security-list-retentionlabels
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import admin_username, client_id, tenant


def _client() -> GraphClient:
    return (
        GraphClient(tenant=tenant)
        .with_token_interactive(client_id, admin_username)
        .require_role("Compliance Administrator", "Global Administrator")
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="List retention labels")
    parser.add_argument("--in-use", action="store_true", help="Show only labels applied to content")
    args = parser.parse_args()

    client = _client()
    labels = client.security.labels.retention_labels.get().execute_query()
    if args.in_use:
        labels = [label for label in labels if label.is_in_use]

    print(f"Retention labels ({len(labels)}):")
    for label in labels:
        print(f"  {label.display_name:40s}  trigger={label.retention_trigger}  in_use={label.is_in_use}")


if __name__ == "__main__":
    main()
