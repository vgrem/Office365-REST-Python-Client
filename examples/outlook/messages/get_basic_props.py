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

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)
user = client.users.get_by_principal_name(test_user_principal_name)
messages = user.messages.select(["id", "subject"]).top(10).get().execute_query()
for message in messages:
    print(message.subject)
