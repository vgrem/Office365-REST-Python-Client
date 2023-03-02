import os
import tempfile

from examples import acquire_token_by_client_credentials, sample_user_principal_name
from office365.graph_client import GraphClient
from office365.outlook.mail.messages.message import Message

client = GraphClient(acquire_token_by_client_credentials)
# requires Mail.ReadWrite permission
user = client.users[sample_user_principal_name]
messages = user.messages.select(["id"]).top(2).get().execute_query()
with tempfile.TemporaryDirectory() as local_path:
    for message in messages:  # type: Message
        with open(os.path.join(local_path, message.id + ".eml"), 'wb') as local_file:
            message.download(local_file).execute_query()  # download MIME representation of a message
        print("Message downloaded into {0}".format(local_file.name))
