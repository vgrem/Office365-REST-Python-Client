"""
Demonstrates how to read messages (basic properties) in user mailbox

"""

from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_client_secret,
    test_tenant,
    test_user_principal_name,
)

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
user = client.users[test_user_principal_name]
messages = user.messages.select(["id", "subject"]).top(10).get().execute_query()
for message in messages:
    print(message.subject)
