import sys

from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

# The example is adapted from https://learn.microsoft.com/en-us/graph/api/message-delta?view=graph-rest-1.0
from office365.outlook.mail.messages.message import Message


client = GraphClient(acquire_token_by_username_password)
messages = client.me.messages.top(1).get().execute_query()
if len(messages) == 0:
    sys.exit("No messages found")
first_message = messages[0]  # type: Message
first_message.set_property("isRead", True).update().execute_query()
