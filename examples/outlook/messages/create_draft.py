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
    test_username,
)

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)
draft_message = (
    client.users[test_user_principal_name]
    .messages.add(
        subject="Meet for lunch?",
        body="The new cafeteria is open.",
        to_recipients=["fannyd@contoso.onmicrosoft.com", test_username],
    )
    .execute_query()
)
print(draft_message)
