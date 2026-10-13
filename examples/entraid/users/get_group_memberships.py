"""
Get a user's group memberships.

Lists all groups a user is a direct member of via the ``memberOf``
relationship. For transitive (nested) membership, see ``transitiveMemberOf``.

https://learn.microsoft.com/en-us/graph/api/user-list-memberof

https://learn.microsoft.com/en-us/graph/api/resources/user

Requires delegated permission ``User.Read.All``.
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(test_client_id, test_username, test_password)

user = client.users.get_by_principal_name("user@contoso.onmicrosoft.com")
groups = user.member_of.get().execute_query()

for g in groups:
    print(f"{g.entity_type_name:<45s}  {g.display_name or ''}")
