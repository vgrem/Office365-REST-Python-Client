"""
List the members of an Entra ID directory role.

Directory role members are polymorphic ``directoryObject`` entries: each member
is mapped to its concrete type (``User``, ``Group``, ``Device``, ...) based on
the ``@odata.type`` reported by Graph.

Requires delegated permission ``RoleManagement.Read.Directory``
(or ``Directory.Read.All``).

    python list_role_members.py
    python list_role_members.py --role "Security Administrator"

https://learn.microsoft.com/en-us/graph/api/directoryrole-list-members
"""

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    parser = argparse.ArgumentParser(description="List members of a directory role")
    parser.add_argument(
        "--role",
        default="Global Administrator",
        help="role display name, e.g. 'Security Administrator' (default: 'Global Administrator')",
    )
    args = parser.parse_args()

    client = (
        GraphClient(tenant=tenant)
        .with_client_secret(client_id, client_secret)
        .require_application_permission(
            "RoleManagement.Read.Directory",
            "RoleManagement.ReadWrite.Directory",
            "Directory.Read.All",
            "Directory.ReadWrite.All",
        )
    )
    role = client.directory_roles.find_by_name(args.role, required=True).execute_query()
    members = role.members.get().execute_query()
    print(f"Members of '{role.display_name}' ({len(members)}):")
    for member in members:
        print(f"  {type(member).__name__:<8} {member}")


if __name__ == "__main__":
    main()
