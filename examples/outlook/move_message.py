import sys

from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.outlook.mail.messages.message import Message

client = GraphClient(acquire_token_by_username_password)

my_mail_folders = client.me.mail_folders.filter("displayName eq 'Archive'").get().execute_query()
if len(my_mail_folders) == 0:
    sys.exit("Mail folder not found")

message = client.me.messages.add()  # type: Message
message.subject = "Meet for lunch?"
message.body = "The new cafeteria is open."
message.to_recipients = ["fannyd@contoso.onmicrosoft.com"]
message.move(my_mail_folders[0].id).execute_query()
print("Draft message is created && moved into {0} folder".format(my_mail_folders[0].display_name))
