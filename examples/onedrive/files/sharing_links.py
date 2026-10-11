"""
Create, list and remove sharing links for a file.

A sharing link is a permission granted to whoever holds the URL — ``anonymous``
(anyone with the link) or ``organization`` (signed-in colleagues). Use a link
when you don't know the recipients; see `sharing_invitations.py` for the
named-recipient twin.

Requires delegated permission ``Files.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/driveitem-createlink
https://learn.microsoft.com/en-us/onedrive/developer/rest-api/concepts/sharing
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Create and remove sharing links for a file")
    parser.add_argument("--keep", action="store_true", help="keep the sample file")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    item = client.me.drive.root.upload(f"{create_unique_name('link')}.txt", b"link me\n").execute_query()

    view = item.create_link("view", "anonymous").execute_query()
    print(f"anonymous view   : {view.link.webUrl}")

    edit = item.create_link("edit", "organization").execute_query()
    print(f"organization edit: {edit.link.webUrl}")

    permissions = item.permissions.get().execute_query()
    print(f"\npermissions ({len(permissions)}):")
    for permission in permissions:
        link = permission.link.webUrl if permission.link else ""
        print(f"  {permission.id}  roles={', '.join(permission.roles)}  {link}")

    # Removing a link = deleting the permission that backs it.
    edit.delete_object().execute_query()
    print("\nRemoved the organization edit link.")

    if not args.keep:
        item.delete_object().execute_query()
        print("Cleaned up.")


if __name__ == "__main__":
    main()
