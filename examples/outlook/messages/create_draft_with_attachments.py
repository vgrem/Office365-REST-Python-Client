import base64

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

with open(r"../../data/Sample.pdf", "rb") as f:
    content = base64.b64encode(f.read()).decode()
client = GraphClient(acquire_token_by_username_password)
client.me.messages.add(
    subject="Meet for lunch?",
    body="The new cafeteria is open.",
    to_recipients=["fannyd@contoso.onmicrosoft.com"],
).add_file_attachment(
    "Sample.pdf", content_type="application/pdf", base64_content=content
).execute_query()
