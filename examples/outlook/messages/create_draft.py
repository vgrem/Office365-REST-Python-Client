"""
Create a draft of a new message

https://learn.microsoft.com/en-us/graph/api/user-post-messages?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_client_secret,
    test_tenant,
    test_user_principal_name,
)

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
client.users[test_user_principal_name].messages.add(
    subject="Meet for lunch?",
    body="The new cafeteria is open.",
    to_recipients=["fannyd@contoso.onmicrosoft.com"],
).send().execute_query()
