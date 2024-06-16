"""
Retrieve the properties of a message.

Requires Mail.Read permission at least

https://learn.microsoft.com/en-us/graph/api/message-get?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
messages = client.me.messages.select(["subject", "body"]).top(10).get().execute_query()
for message in messages:
    print(message.subject)
