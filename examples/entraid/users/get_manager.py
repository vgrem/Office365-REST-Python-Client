"""
Get a user's manager.

Retrieves the manager assigned to a user and prints the manager's
``displayName``.

https://learn.microsoft.com/en-us/graph/api/user-list-manager

https://learn.microsoft.com/en-us/graph/api/resources/user

Requires delegated permission ``User.Read.All``.
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(test_client_id, test_username, test_password)

user = client.users.get_by_principal_name("user@contoso.onmicrosoft.com")
manager = user.manager.select(["displayName"]).get().execute_query()

print(f"Manager: {manager.display_name}")
