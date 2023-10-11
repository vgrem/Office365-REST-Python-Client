"""
Mark message as read example

https://learn.microsoft.com/en-us/graph/api/message-update?view=graph-rest-1.0&tabs=http
"""

import sys

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
messages = client.me.messages.top(1).get().execute_query()
if len(messages) == 0:
    sys.exit("No messages found")
first_message = messages[0]  # type: Message
first_message.set_property("isRead", True).update().execute_query()
