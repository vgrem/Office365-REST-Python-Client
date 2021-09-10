from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.outlook.mail.messages.message import Message

# The example is adapted from https://docs.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0

client = GraphClient(acquire_token_by_username_password)

message = client.me.messages.new()  # type: Message
message.subject = "Meet for lunch?"
message.body = "The new cafeteria is open."
message.to_recipients = ["fannyd@contoso.onmicrosoft.com"]

client.me.send_mail(message).execute_query()
