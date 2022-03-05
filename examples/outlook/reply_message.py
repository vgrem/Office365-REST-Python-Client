import sys

from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.outlook.mail.messages.message import Message

# The example is adapted from https://docs.microsoft.com/en-us/graph/api/message-reply?view=graph-rest-1.0
from tests import settings

client = GraphClient(acquire_token_by_username_password)

messages = client.me.messages.top(1).get().execute_query()
if len(messages) == 0:
    sys.exit("No messages were found")

comment = "Fanny, would you join us next time?"
message = client.me.messages.new()  # type: Message
message.to_recipients = ["fannyd@contoso.onmicrosoft.com", settings.get('user_credentials', "username")]
first_message = messages[0]  # type: Message
first_message.reply(message, comment).execute_query()
