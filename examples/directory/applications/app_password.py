"""
Adds a strong password or secret to an application.
https://learn.microsoft.com/en-us/graph/api/application-addpassword?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import (
    test_client_credentials,
    test_client_id,
    test_password,
    test_tenant,
    test_username,
)

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
target_app = client.applications.get_by_app_id(test_client_credentials.clientId)
result = target_app.add_password("Password friendly name").execute_query()
print(result.value)
