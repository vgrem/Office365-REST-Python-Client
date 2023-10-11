"""
Retrieve the properties of a message.

Requires Mail.Read permission at least

https://learn.microsoft.com/en-us/graph/api/message-get?view=graph-rest-1.0&tabs=http
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
messages = client.me.messages.select(["subject", "body"]).top(1).get().execute_query()
for message in messages:  # type: Message
    print(message.body.content)
