"""
Assign manager

https://learn.microsoft.com/en-us/graph/api/user-post-manager?view=graph-rest-1.0&tabs=http
"""
from office365.graph_client import GraphClient
from tests import test_user_principal_name
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
user = client.users.get_by_principal_name(test_user_principal_name)
manager = client.me.assign_manager(user).get().execute_query()
print("User manager has been assigned")
