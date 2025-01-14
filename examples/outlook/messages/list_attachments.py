"""
List attachments

https://learn.microsoft.com/en-us/graph/api/message-list-attachments?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
messages = (
    client.me.messages.filter("hasAttachments eq true")
    .expand(["attachments"])
    .top(10)
    .get()
    .execute_query()
)

for message in messages:
    for attachment in message.attachments:
        print("Message: {0}, Attachment: {1}".format(message.subject, attachment.name))
