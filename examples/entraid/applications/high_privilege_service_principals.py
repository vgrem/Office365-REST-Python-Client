"""
Find service principals holding high-privilege directory roles.

Service principals (app registrations) can be granted built-in directory
roles such as Global Administrator. This script enumerates service principals
and reports the ones holding a high-privilege role assignment.

Requires delegated permissions ``Directory.Read.All`` and
``AppRoleAssignment.Read.All``.

https://learn.microsoft.com/en-us/graph/api/serviceprincipal-list
https://learn.microsoft.com/en-us/graph/api/serviceprincipal-list-approleassignments
https://learn.microsoft.com/en-us/graph/api/resources/approleassignment
"""

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

# Resource display names of the directory roles application (formerly Azure AD).
DIRECTORY_ROLE_RESOURCES = {"Microsoft Entra ID", "Microsoft Azure Active Directory"}

# Built-in directory role appRoleIds (on the "Microsoft Entra ID" service
# principal) considered high privilege when granted to a service principal.
HIGH_PRIVILEGE_ROLES = {
    "62e90394-69f5-4237-9190-012177145e10": "Global Administrator",
    "e8611ab3-c189-46e8-94e1-60213ab1f814": "Privileged Role Administrator",
    "9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3": "Application Administrator",
    "158c047a-c907-4556-b7ef-446551a6b5f7": "Cloud Application Administrator",
    "29232cdf-8323-42fc-9f8e-4f9b9c3d4e5f": "Exchange Administrator",
    "f28a1f50-f6e7-4571-818b-13512edef760": "SharePoint Administrator",
    "fe930be7-5e62-47db-91af-98c3a49a38b1": "User Administrator",
}


def main():
    parser = argparse.ArgumentParser(description="Service principals holding high-privilege directory roles")
    parser.add_argument(
        "--all-roles",
        action="store_true",
        help="report every directory-role assignment, not only high-privilege roles",
    )
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    findings = []
    for sp in client.service_principals.select(["id", "displayName"]).get().execute_query():
        roles = set()
        for assignment in sp.app_role_assignments.get().execute_query():
            if assignment.resource_display_name not in DIRECTORY_ROLE_RESOURCES:
                continue
            app_role_id = assignment.app_role_id or ""
            role = HIGH_PRIVILEGE_ROLES.get(app_role_id, app_role_id)
            if args.all_roles or role in HIGH_PRIVILEGE_ROLES.values():
                roles.add(role)
        if roles:
            findings.append((sp.display_name, roles))

    if not findings:
        print("No service principals with directory-role assignments found.")
        return

    for name, roles in findings:
        print(f"  {name:50s} {', '.join(sorted(roles))}")
    print(f"\n{len(findings)} service principal(s) hold directory roles")


if __name__ == "__main__":
    main()
