"""
Send a sharing invitation

This example sends a sharing invitation to a user with email address "ryan@contoso.com" with a message about a
file being collaborated on. The invitation grants Ryan read-write access to the file.

https://learn.microsoft.com/en-us/graph/api/driveitem-invite?view=graph-rest-1.0
"""
import json
from datetime import datetime, timedelta

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

file_name = "Financial Sample.xlsx"
client = GraphClient(acquire_token_by_username_password)
# upload_sample_files(client.me.drive)
file_item = client.me.drive.root.get_by_path(file_name)
expired = datetime.utcnow() + timedelta(days=1)
permissions = file_item.invite(
    recipients=["ryan@contoso.com"],
    message="Here's the file that we're collaborating on.",
    roles=["read"],
    expiration_datetime=None,
    password="password123").execute_query()
print(json.dumps(permissions.to_json(), indent=4))
