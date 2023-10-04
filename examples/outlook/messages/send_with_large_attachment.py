"""
Demonstrates how to upload large attachment to Outlook message

https://learn.microsoft.com/en-us/graph/api/attachment-createuploadsession?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)

local_path = "../../../tests/data/big_buck_bunny.mp4"


def print_progress(range_pos):
    print("{0} bytes uploaded".format(range_pos))


message = (
    client.me.messages.add(
        subject="Meet for lunch?",
        body="The new cafeteria is open.",
        to_recipients=["fannyd@contoso.onmicrosoft.com"],
    )
    .upload_attachment(local_path, print_progress)
    .execute_query()
)
message.send().execute_query()
