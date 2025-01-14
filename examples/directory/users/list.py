"""
List users

https://learn.microsoft.com/en-us/graph/api/user-list?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
users = client.users.get().top(10).execute_query()
for u in users:
    print(u.user_principal_name)
