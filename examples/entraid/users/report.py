"""
Report: sample users and accounts without an assigned license.

Common identity-hygiene scenarios:
  - sample users to check their core attributes
  - find accounts that have no license assigned

Requires application permission ``User.Read.All``.

https://learn.microsoft.com/en-us/graph/api/user-list
https://learn.microsoft.com/en-us/graph/api/user-list-licensedetails
"""

from __future__ import annotations

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main() -> None:
    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    # 1. Sample users and their core attributes
    users = client.users.select(["id", "displayName", "userPrincipalName"]).top(20).get().execute_query()
    print("Users:")
    print(users.to_string())

    # 2. Users without an assigned license
    unlicensed = client.users.get_unlicensed().top(10).select(["id", "displayName", "userPrincipalName"]).execute_query()
    print(f"\nUnlicensed accounts ({len(unlicensed)}):")
    print(unlicensed.to_string())


if __name__ == "__main__":
    main()
