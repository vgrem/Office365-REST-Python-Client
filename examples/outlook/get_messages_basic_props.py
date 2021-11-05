from examples import acquire_token_by_client_credentials, test_user_principal_name
from office365.graph_client import GraphClient
from office365.outlook.mail.messages.message import Message

# Demonstrates how to read messages (only basic properties!) in user mailbox

client = GraphClient(acquire_token_by_client_credentials)
# requires Mail.ReadBasic.All permission
user = client.users[test_user_principal_name]
messages = user.messages.select(["id", "subject"]).top(10).get().execute_query()
for message in messages:  # type: Message
    print(message.id)
