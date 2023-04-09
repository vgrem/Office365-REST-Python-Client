from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

# The example is adapted from https://docs.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0

client = GraphClient(acquire_token_by_username_password)
client.me.send_mail(
    subject="Meet for lunch?",
    body="The new cafeteria is open.",
    to_recipients=["fannyd@contoso.onmicrosoft.com"]
).add_file_attachment("attachment.txt", "--Some content goes here--", "text/plain").execute_query()
