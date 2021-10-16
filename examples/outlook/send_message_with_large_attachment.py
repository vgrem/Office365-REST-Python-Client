from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.outlook.mail.messages.message import Message

client = GraphClient(acquire_token_by_username_password)

message = client.me.messages.add()  # type: Message
message.subject = "Meet for lunch?"
message.body = "The new cafeteria is open."
message.to_recipients = ["fannyd@contoso.onmicrosoft.com"]

local_path = "../../tests/data/big_buck_bunny.mp4"
file_attachment = message.upload_attachment(local_path)
client.execute_query()
# client.me.send_mail(message).execute_query()
print("Email sent")
