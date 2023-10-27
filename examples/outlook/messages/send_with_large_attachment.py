"""
Demonstrates how send e message with large attachment to Outlook message

https://learn.microsoft.com/en-us/graph/api/attachment-createuploadsession?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_user_principal_name_alt
from tests.graph_case import acquire_token_by_username_password


def print_progress(range_pos):
    print("{0} bytes uploaded".format(range_pos))


client = GraphClient(acquire_token_by_username_password)
local_path = "../../../tests/data/big_buck_bunny.mp4"
message = (
    (
        client.me.messages.add(
            subject="Meet for lunch?",
            body="The new cafeteria is open.",
            to_recipients=[
                "fannyd@contoso.onmicrosoft.com",
                test_user_principal_name_alt,
            ],
        ).upload_attachment(local_path, print_progress)
    )
    .send()
    .execute_query()
)
