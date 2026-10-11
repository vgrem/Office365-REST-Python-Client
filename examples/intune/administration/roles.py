"""
Intune RBAC: built-in and custom roles, their assignments, and effective access.

Intune has its own role-based access control, separate from Entra ID directory
roles. A *role definition* is a named set of permissions; a *role assignment*
binds one to a group within a scope tag. This is the "administration" layer that
decides who may change what.

    python roles.py                  # list role definitions
    python roles.py --assignments    # + who holds each role
    python roles.py --effective      # + the caller's effective permissions

Requires delegated permission ``DeviceManagementRBAC.Read.All``.

https://learn.microsoft.com/en-us/graph/api/intune-rbac-devicemanagement-list-roledefinitions
https://learn.microsoft.com/en-us/graph/api/intune-rbac-devicemanagement-list-roleassignments
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Intune role-based access control")
    parser.add_argument("--assignments", action="store_true", help="Also list role assignments")
    parser.add_argument("--effective", action="store_true", help="Also show the caller's effective permissions")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    dm = client.device_management

    try:
        definitions = list(dm.role_definitions.get_all().execute_query())
        print(f"Role definitions ({len(definitions)}):")
        for definition in definitions:
            kind = "built-in" if definition.is_built_in else "custom"
            print(
                f"  {definition.display_name or '(unnamed)':30s} [{kind:8s}]"
                f"  {len(definition.role_permissions)} permission set(s)"
            )
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Grant admin consent for DeviceManagementRBAC.Read.All and re-run.")
        return

    if args.assignments:
        try:
            assignments = list(dm.role_assignments.get_all().execute_query())
            print(f"\nRole assignments ({len(assignments)}):")
            for assignment in assignments:
                members = list(assignment.members)
                print(f"  {assignment.display_name or '(unnamed)':30s} members: {', '.join(members) or '(none)'}")
        except ClientRequestException as exc:
            print(f"\n[skipped] assignments: {exc.code}")

    if args.effective:
        try:
            permissions = dm.get_effective_permissions().execute_query()
            print(f"\nEffective permissions ({len(permissions)} set(s)):")
            for permission in permissions:
                for action in permission.resourceActions:
                    allowed = ", ".join(action.allowedResourceActions)
                    print(f"  allowed: {allowed or '(none)'}")
        except ClientRequestException as exc:
            print(f"\n[skipped] effective permissions: {exc.code}")


if __name__ == "__main__":
    main()
