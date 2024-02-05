"""
Retrieve a list of licenseDetails objects for enterprise users.

https://learn.microsoft.com/en-us/graph/api/user-list-licensedetails?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_password,
    test_tenant,
    test_username,
)

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
result = client.me.license_details.get().execute_query()
for details in result:
    print(details)
