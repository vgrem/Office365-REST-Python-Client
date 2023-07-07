"""
Demonstrates how to read messages (basic properties) in user mailbox

"""

from office365.graph_client import GraphClient
from office365.outlook.mail.messages.message import Message
from tests import test_user_principal_name
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
user = client.users[test_user_principal_name]
messages = user.messages.select(["id", "subject"]).top(10).get().execute_query()
for message in messages:  # type: Message
    print(message.id)
