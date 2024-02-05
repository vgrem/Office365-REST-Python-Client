"""
Assign manager

https://learn.microsoft.com/en-us/graph/api/user-post-manager?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_password,
    test_tenant,
    test_user_principal_name,
    test_username,
)

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
manager = client.users.get_by_principal_name(test_user_principal_name)
client.me.assign_manager(manager).get().execute_query()
print("User manager has been assigned")
