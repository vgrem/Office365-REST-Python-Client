"""
Send the message specified in the request body using either JSON or MIME format.

The example is adapted from https://docs.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from office365.outlook.mail.item_body import ItemBody
from tests import (
    test_client_id,
    test_password,
    test_tenant,
    test_user_principal_name_alt,
    test_username,
)

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
client.me.send_mail(
    subject="Meet for lunch?",
    body=ItemBody.html("<h1>The new cafeteria is open.</h1>"),
    to_recipients=["fannyd@contoso.onmicrosoft.com", test_user_principal_name_alt],
).execute_query()
