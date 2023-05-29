"""
Reply to the sender of a message using either JSON or MIME format.

The example is adapted from https://docs.microsoft.com/en-us/graph/api/message-reply?view=graph-rest-1.0
"""

import sys
from office365.graph_client import GraphClient
from office365.outlook.mail.messages.message import Message
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
messages = client.me.messages.top(1).get().execute_query()
if len(messages) == 0:
    sys.exit("No messages were found")

first_message = messages[0]  # type: Message
first_message.reply(comment="Fanny, would you join us next time?").execute_query()
