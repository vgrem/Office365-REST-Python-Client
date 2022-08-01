from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

client = GraphClient(acquire_token_by_username_password)

local_path = "../../tests/data/Sample.txt"
# local_path = "../../tests/data/big_buck_bunny.mp4"

client.me.messages.add(
    subject="Meet for lunch?",
    body="The new cafeteria is open.",
    to_recipients=["fannyd@contoso.onmicrosoft.com", "vvgrem@gmail.com"]
).upload_attachment(local_path).send().execute_query()
print("Email has been sent.")
