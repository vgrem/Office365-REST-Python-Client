import os
import tempfile

from examples import acquire_token_by_client_credentials, test_user_principal_name
from office365.graph_client import GraphClient
from office365.outlook.mail.attachments.attachment import Attachment
from office365.outlook.mail.messages.message import Message

# Purpose: demonstrates how to download message attachments
# Permissions: requires Mail.ReadWrite

client = GraphClient(acquire_token_by_client_credentials)
user = client.users[test_user_principal_name]
messages = user.messages.filter("hasAttachments eq true").expand(["attachments"]).top(10).get().execute_query()
with tempfile.TemporaryDirectory() as local_path:
    for message in messages:  # type: Message
        for attachment in message.attachments:  # type: Attachment
            with open(os.path.join(local_path, attachment.name), 'wb') as local_file:
                attachment.download(local_file).execute_query()
            print("Message attachment downloaded into {0}".format(local_file.name))
