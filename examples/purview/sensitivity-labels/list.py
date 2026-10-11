"""
Sensitivity labels — list the labels published in the tenant.

Sensitivity labels classify content by confidentiality (Public, Internal,
Confidential, Highly Confidential, ...) and travel with the content. This script
inventories the labels; to *apply* one to a SharePoint file, see
``examples/sharepoint/sites/assign_sensitivity_label.py``.

    python list.py
    python list.py --detail

Requires delegated permission ``InformationProtectionPolicy.Read.All`` **and**
the Compliance Administrator (or Global Administrator) role.

https://learn.microsoft.com/en-us/graph/api/informationprotectionpolicy-list-labels
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import admin_username, client_id, tenant

_SCOPES = ["https://graph.microsoft.com/InformationProtectionPolicy.Read.All"]


def _client() -> GraphClient:
    return (
        GraphClient(tenant=tenant, scopes=_SCOPES)
        .with_token_interactive(client_id, admin_username)
        .require_role("Compliance Administrator", "Global Administrator")
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="List sensitivity labels")
    parser.add_argument("--detail", action="store_true", help="Show priority and description")
    args = parser.parse_args()

    client = _client()
    labels = client.security.data_security_and_governance.sensitivity_labels.get().execute_query()
    print(f"Sensitivity labels ({len(labels)}):\n")

    for label in labels:
        if args.detail:
            print(f"  {label.display_name:30s}  priority={label.priority}  {label.description}")
        else:
            print(f"  {label.display_name:30s}  id: {label.id}")


if __name__ == "__main__":
    main()
