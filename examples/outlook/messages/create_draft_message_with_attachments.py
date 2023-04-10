import base64

from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient


# Multple "add_file_attachment" calls can be chained before "execute_query" to add multiple attachments

with open(r"path\to\file\test.pdf", "rb") as f:
    content = base64.b64encode(f.read()).decode()
client = GraphClient(acquire_token_by_username_password)
client.me.messages.add(
    subject="Meet for lunch?",
    body="The new cafeteria is open.",
    to_recipients=["fannyd@contoso.onmicrosoft.com"]
).add_file_attachment("attachment.txt", content_type="application/pdf", base64_content=content).execute_query()
