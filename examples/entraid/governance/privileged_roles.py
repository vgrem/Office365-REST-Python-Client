"""
Privileged roles - list active PIM directory role assignments.

Shows which principal (user, group or service principal) is actively assigned
to each directory role, via the role management API. This is the tenant-wide
view that complements ``directory_roles`` (which lists *activated* roles).

Requires application permission ``Directory.Read.All``.

Reference:
    https://learn.microsoft.com/en-us/graph/api/rbacapplication-list-roleassignments
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    client = _client().require_application_permission("Directory.Read.All")

    assignments = client.role_management.directory.role_assignments.expand(["roleDefinition"]).get().execute_query()
    print(f"Active directory role assignments ({len(assignments)}):\n")
    for assignment in assignments:
        role = assignment.role_definition.display_name if assignment.role_definition else "?"
        scope = assignment.directory_scope_id or "/"
        print(f"  principal={assignment.principal_id or '?':40s}  role={role or '?':35s}  scope={scope}")


if __name__ == "__main__":
    main()
