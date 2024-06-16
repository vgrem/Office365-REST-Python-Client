"""
Downloads MIME representation of a message

https://learn.microsoft.com/en-us/graph/outlook-get-mime-message
Requires Mail.ReadWrite permission
"""

import os
import tempfile

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
messages = client.me.messages.select(["id", "subject"]).top(1).get().execute_query()
with tempfile.TemporaryDirectory() as local_path:
    for message in messages:
        with open(os.path.join(local_path, message.subject + ".eml"), "wb") as f:
            message.download(f).execute_query()

        print("Message downloaded into {0}".format(f.name))
