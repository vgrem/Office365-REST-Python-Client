"""
The smallest communications script: connect and read your own presence.

If this works, your app registration and consent are fine — move on to the
``presence/`` folder.

Requires the delegated permission ``Presence.Read``.
"""

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main():
    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    presence = client.me.presence.get().execute_query()
    print(f"You are {presence.availability} / {presence.activity}")


if __name__ == "__main__":
    main()
