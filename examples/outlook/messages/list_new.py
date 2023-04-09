from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

# The example is adapted from https://learn.microsoft.com/en-us/graph/api/message-delta?view=graph-rest-1.0
from office365.outlook.mail.messages.message import Message


client = GraphClient(acquire_token_by_username_password)
messages = client.me.mail_folders["Inbox"].messages.delta.change_type("created").get().execute_query()
for m in messages:  # type: Message
    print(m.subject)
