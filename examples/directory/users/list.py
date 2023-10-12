"""
List users

https://learn.microsoft.com/en-us/graph/api/user-list?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
users = client.users.get().top(10).execute_query()
for u in users:
    print(u.user_principal_name)
