"""
Get a set of messages that have been added in a specified folder.

The example is adapted from https://learn.microsoft.com/en-us/graph/api/message-delta?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
messages = (
    client.me.mail_folders["Inbox"]
    .messages.delta.change_type("created")
    .get()
    .execute_query()
)
for m in messages:
    print(m.subject)
