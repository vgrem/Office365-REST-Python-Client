from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

# The example is adapted from https://docs.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0
from office365.outlook.mail.messages.message import Message
from tests import settings

client = GraphClient(acquire_token_by_username_password)
messages = client.me.messages.get().execute_query()
for m in messages:  # type: Message
    print(m.subject)
