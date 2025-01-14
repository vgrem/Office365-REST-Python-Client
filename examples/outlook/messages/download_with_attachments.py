"""
Demonstrates how to download message attachments

https://learn.microsoft.com/en-us/graph/api/attachment-get?view=graph-rest-1.0
"""

import os
import tempfile

from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_client_secret,
    test_tenant,
    test_user_principal_name,
)

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)
user = client.users[test_user_principal_name]
messages = (
    user.messages.filter("hasAttachments eq true")
    .expand(["attachments"])
    .top(10)
    .get()
    .execute_query()
)
with tempfile.TemporaryDirectory() as local_path:
    for message in messages:
        for attachment in message.attachments:
            with open(os.path.join(local_path, attachment.name), "wb") as local_file:
                attachment.download(local_file).execute_query()
            print("Message attachment downloaded into {0}".format(local_file.name))
