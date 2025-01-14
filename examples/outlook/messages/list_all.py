"""
Get the messages in the signed-in user's mailbox

# The example is adapted from https://learn.microsoft.com/en-us/graph/api/user-list-messages
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
messages = client.me.messages.get().top(10).execute_query()
for m in messages:
    print(m.subject)
