import sys

from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.outlook.mail.messages.message import Message

# The example is adapted from https://docs.microsoft.com/en-us/graph/api/message-reply?view=graph-rest-1.0

client = GraphClient(acquire_token_by_username_password)

messages = client.me.messages.top(1).get().execute_query()
if len(messages) == 0:
    sys.exit("No messages were found")

first_message = messages[0]  # type: Message
first_message.reply(
    comment="Fanny, would you join us next time?"
).execute_query()
