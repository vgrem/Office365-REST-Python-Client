"""
Send a sharing invitation

This example sends a sharing invitation to a user with email address "ryan@contoso.com" with a message about a
file being collaborated on. The invitation grants Ryan read-write access to the file.

https://learn.microsoft.com/en-us/graph/api/driveitem-invite?view=graph-rest-1.0
"""

from datetime import datetime, timedelta

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

file_name = "Financial Sample.xlsx"
client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
file_item = client.me.drive.root.get_by_path(file_name)
expired = datetime.utcnow() + timedelta(days=1)
permissions = file_item.invite(
    recipients=["ryan@contoso.com"],
    message="Here's the file that we're collaborating on.",
    roles=["read"],
    expiration_datetime=None,
    password="password123",
).execute_query()
for perm in permissions:
    print(perm.granted_to_identities)
