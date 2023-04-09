from examples import acquire_token_by_client_credentials, sample_user_principal_name
from office365.graph_client import GraphClient
from office365.outlook.mail.messages.message import Message

client = GraphClient(acquire_token_by_client_credentials)
# requires Mail.Read permission
user = client.users[sample_user_principal_name]
messages = user.messages.select(["subject", "body"]).top(10).get().execute_query()
for message in messages:  # type: Message
    print(message.body.content)
