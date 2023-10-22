"""
Get a set of messages that have been added in a specified folder.

The example is adapted from https://learn.microsoft.com/en-us/graph/api/message-delta?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from office365.outlook.mail.messages.message import Message
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
messages = (
    client.me.mail_folders["Inbox"]
    .messages.delta.change_type("created")
    .get()
    .execute_query()
)
for m in messages:
    print(m.subject)
