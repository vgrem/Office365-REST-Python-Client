"""
Invite specific people to a file (grant access by email).

When you know the recipients, invite them instead of publishing a link: Graph
grants the permission and (optionally) emails them. ``roles`` is one of
``read`` / ``write`` / ``owner``.
you don't know who needs access yet (see `sharing_links.py`).

Requires delegated permission ``Files.ReadWrite`` and a valid recipient UPN.

https://learn.microsoft.com/en-us/graph/api/driveitem-invite
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Invite a user to a file")
    parser.add_argument("--user", required=True, help="UPN of the person to invite")
    parser.add_argument("--role", default="read", choices=["read", "write", "owner"], help="access level to grant")
    parser.add_argument("--keep", action="store_true", help="keep the sample file")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    item = client.me.drive.root.upload(f"{create_unique_name('invite')}.txt", b"invite me\n").execute_query()

    invitation = item.invite(
        [args.user],
        roles=[args.role],
        send_invitation=True,
        message="Here's the file you requested.",
    ).execute_query()
    print(f"Invited {args.user} with role={args.role}")
    print(f"  permission id: {invitation.id}  status: {invitation.invitation.status}")

    # The invitation shows up as a permission on the item.
    permissions = item.permissions.get().execute_query()
    print(f"\npermissions ({len(permissions)}):")
    for permission in permissions:
        print(f"  {permission.id}  roles={', '.join(permission.roles)}")

    if not args.keep:
        item.delete_object().execute_query()
        print("Cleaned up.")


if __name__ == "__main__":
    main()
