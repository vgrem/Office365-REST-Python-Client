"""
List the users who hold privileged Microsoft Entra directory roles.

Answers "who are my admins?" for access reviews and break-glass audits. Every
*activated* directory role is expanded to its members, and the result is
inverted so each user is shown once with the full set of roles they hold.

Roles are marked with a flag when they are highly privileged (for example
``Global Administrator``, which can do anything in the tenant).

Usage:

    python privileged_users.py                 # users holding any activated role
    python privileged_users.py --role "Global Administrator"   # one role only

Requires application permission ``Directory.Read.All`` (delegated
``RoleManagement.Read.Directory`` also works).

Reference:
    https://learn.microsoft.com/en-us/graph/api/directoryrole-list
    https://learn.microsoft.com/en-us/graph/api/directoryrole-list-members
    https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
"""

from __future__ import annotations

import argparse
from collections import defaultdict

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

#: Roles that grant the broadest control over the tenant or security controls.
HIGH_IMPACT_ROLES = {
    "Global Administrator",
    "Privileged Role Administrator",
    "Privileged Authentication Administrator",
    "Application Administrator",
    "Cloud Application Administrator",
    "Authentication Administrator",
    "Security Administrator",
    "Conditional Access Administrator",
    "Partner Tier2 Support",
}


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def _display(member) -> str:
    """Human-readable label for a role member (user, group or service principal)."""
    if getattr(member, "user_principal_name", None):
        return f"{member.display_name} <{member.user_principal_name}>"
    return f"{member.display_name or '(unnamed)'} [{member.entity_type_name}]"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", help="limit the report to a single role display name")
    args = parser.parse_args()

    client = _client()
    roles = client.directory_roles.get().execute_query()

    users: dict[str, set[str]] = defaultdict(set)
    labels: dict[str, str] = {}
    total_memberships = 0

    for role in roles:
        if args.role and role.display_name != args.role:
            continue
        members = role.members.select(["id", "displayName", "userPrincipalName"]).get().execute_query()
        for member in members:
            users[member.id].add(role.display_name)
            labels[member.id] = _display(member)
            total_memberships += 1

    print(f"Privileged role holders ({len(users)} users, {total_memberships} memberships):\n")
    for user_id, role_names in sorted(users.items(), key=lambda item: (-len(item[1]), labels[item[0]])):
        marks = [f"{r} ⚠" if r in HIGH_IMPACT_ROLES else r for r in sorted(role_names)]
        print(f"  {labels[user_id]}")
        print(f"      {', '.join(marks)}")

    global_admins = [uid for uid, names in users.items() if "Global Administrator" in names]
    if global_admins:
        print(f"\n⚠  {len(global_admins)} user(s) hold Global Administrator — review regularly.")


if __name__ == "__main__":
    main()
