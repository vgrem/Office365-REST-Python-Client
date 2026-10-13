"""
Entitlement management - list access packages and their assignments.

Access packages bundle the resources (groups, apps, SharePoint sites) that a
user can request. This script lists the catalog packages and the assignments
that have been granted from them.

Requires application permission ``EntitlementManagement.Read.All``.
Not every tenant grants it; the script reports a denied request and exits 0.

Reference:
    https://learn.microsoft.com/en-us/graph/api/entitlementmanagement-list-accesspackages
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=20, help="max packages to list")
    args = parser.parse_args()

    client = _client()
    entitlement_management = client.identity_governance.entitlement_management

    try:
        packages = entitlement_management.access_packages.top(args.limit).get().execute_query()
        assignments = entitlement_management.assignments.expand(["accessPackage", "target"]).get().execute_query()
    except ClientRequestException as e:
        print(f"Entitlement management is not available with these credentials:\n  {e}")
        return

    print(f"Access packages ({len(packages)}):\n")
    for package in packages:
        print(f"  {package.display_name or '(unnamed)':40s}  {package.description or ''}")

    print(f"\nAssignments ({len(assignments)}):\n")
    for assignment in assignments:
        package_name = assignment.access_package.display_name if assignment.access_package else "?"
        target = assignment.target
        who = (target.principal_name or target.display_name) if target else None
        print(
            f"  {package_name or '?':40s}  {who or '?':35s}  "
            f"state={assignment.state.name:18s}  expires={assignment.expired_date_time:%Y-%m-%d}"
        )


if __name__ == "__main__":
    main()
