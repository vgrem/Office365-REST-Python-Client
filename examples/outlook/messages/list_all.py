"""
Get the messages in the signed-in user's mailbox

# The example is adapted from https://learn.microsoft.com/en-us/graph/api/user-list-messages
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
messages = client.me.messages.get().execute_query()
for m in messages:  # type: Message
    print(m.subject)
