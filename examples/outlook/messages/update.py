"""
Create a single-value extended property for a message

Demonstrates how to update the properties of a message object.

https://learn.microsoft.com/en-us/graph/api/message-update?view=graph-rest-1.0
"""

import sys

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
messages = client.me.messages.top(1).get().execute_query()
if len(messages) == 0:
    sys.exit("No messages were found")


message = messages[0]
message.subject = "Updated subject"
message.body = "Updated body text"
message.update().execute_query()
