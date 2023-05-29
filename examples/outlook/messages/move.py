"""
Move a message to another folder within the specified user's mailbox.
This creates a new copy of the message in the destination folder and removes the original message.

https://learn.microsoft.com/en-us/graph/api/message-move?view=graph-rest-1.0&tabs=http
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
folder_name = "Archive"
to_folder = client.me.mail_folders[folder_name].get().execute_query()

message = client.me.messages.add(
    subject="Meet for lunch?",
    body="The new cafeteria is open.",
    to_recipients=["fannyd@contoso.onmicrosoft.com"]
)
message.move(to_folder.id).execute_query()
print("Draft message is created && moved into {0} folder".format(to_folder.display_name))
