"""
Manage permissions on a file: break inheritance, grant a user a role,
list role assignments, and reset inheritance.

This is the "share with a specific person" mechanism — the securable-object
role assignments API (as opposed to sharing links).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharing-rest-api
"""

import argparse
import sys

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Manage permissions on a file")
    parser.add_argument(
        "--file-url",
        default="Shared Documents/Financial Sample.xlsx",
        help="server-relative URL of the file",
    )
    parser.add_argument("--user", required=True, help="Login name of the user, e.g. i:0#.f|membership|user@contoso.com")
    parser.add_argument("--role", default="Edit", help="Role to grant, e.g. Read, Edit (default: Edit)")
    parser.add_argument("--reset", action="store_true", help="Reset permission inheritance at the end")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    item = ctx.web.get_file_by_server_relative_url(args.file_url).listItemAllFields
    ctx.load(item, ["Id", "HasUniqueRoleAssignments"]).execute_query()
    print(f"File: {args.file_url}  (unique permissions: {item.has_unique_role_assignments})\n")

    # 1. Break permission inheritance (make permissions unique)
    item.break_role_inheritance().execute_query()
    print("✓ Permission inheritance broken")

    # 2. Resolve the user (principal id)
    user = ctx.web.ensure_user(args.user).execute_query()
    if user.id is None:
        sys.exit(f"User '{args.user}' could not be resolved")
    print(f"✓ User resolved: {user.login_name} (id: {user.id})")

    # 3. Resolve the role definition id
    role_def = ctx.web.role_definitions.get_by_name(args.role).get().execute_query()
    if role_def.id is None:
        sys.exit(f"Role '{args.role}' not found")
    print(f"✓ Role resolved: {role_def.name} (id: {role_def.id})")

    # 4. Grant the user the role
    item.role_assignments.add_role_assignment(user.id, role_def.id).execute_query()
    print(f"✓ Granted '{args.role}' to {args.user}")

    # 5. List current role assignments
    assignments = item.role_assignments.get().execute_query()
    print(f"\nRole assignments ({len(assignments)}):")
    for a in assignments:
        member = a.member
        ctx.load(member, ["Title", "LoginName"]).execute_query()
        print(f"  - {member.login_name or '?'}")

    # 6. Optionally reset inheritance
    if args.reset:
        item.reset_role_inheritance().execute_query()
        print("\n✓ Permission inheritance reset")


if __name__ == "__main__":
    main()
