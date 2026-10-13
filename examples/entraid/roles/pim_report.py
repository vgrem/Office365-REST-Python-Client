"""
PIM (Privileged Identity Management): list role assignments
and report on privileged role members.

Eligible and active role assignments for administrative roles.

Requires delegated permission ``RoleManagement.Read.All``.

https://learn.microsoft.com/en-us/graph/api/rolemanagement-list-roleassignments
"""

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    assignments = client.role_management.directory.role_assignments.get().expand(["roleDefinition"]).execute_query()
    print(f"PIM directory role assignments ({len(assignments)}):")
    for r in assignments:
        print(f"  {r.role_definition.display_name or '?':35s} {r.principal_id}")


if __name__ == "__main__":
    main()
