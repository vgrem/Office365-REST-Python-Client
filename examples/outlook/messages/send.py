"""
Send the message specified in the request body using either JSON or MIME format.

The example is adapted from https://docs.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_user_principal_name
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
client.me.send_mail(
    subject="Meet for lunch?",
    body="The new cafeteria is open.",
    to_recipients=["fannyd@contoso.onmicrosoft.com", test_user_principal_name]
).execute_query()
