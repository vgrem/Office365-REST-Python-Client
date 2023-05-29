"""
Get MIME content of a message

https://learn.microsoft.com/en-us/graph/outlook-get-mime-message
Requires Mail.ReadWrite permission
"""

import os
import tempfile

from office365.graph_client import GraphClient
from office365.outlook.mail.messages.message import Message
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
messages = client.me.messages.select(["id"]).top(2).get().execute_query()
with tempfile.TemporaryDirectory() as local_path:
    for message in messages:  # type: Message
        with open(os.path.join(local_path, message.id + ".eml"), 'wb') as local_file:
            message.download(local_file).execute_query()  # download MIME representation of a message
        print("Message downloaded into {0}".format(local_file.name))
