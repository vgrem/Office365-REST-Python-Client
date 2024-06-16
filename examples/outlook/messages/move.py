"""
Move a message to another folder within the specified user's mailbox.
This creates a new copy of the message in the destination folder and removes the original message.

https://learn.microsoft.com/en-us/graph/api/message-move?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
folder_name = "Archive"
to_folder = client.me.mail_folders[folder_name]

message = client.me.messages.add(
    subject="Meet for lunch?",
    body="The new cafeteria is open.",
    to_recipients=["fannyd@contoso.onmicrosoft.com"],
)
message.move(to_folder).execute_query()
print("Draft message is created && moved into {0} folder".format(folder_name))
