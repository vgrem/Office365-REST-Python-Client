"""
Example shows a request to retrieve all app role assignments granted to the user
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)

result = client.me.app_role_assignments.get().execute_query()
for assignment in result:
    print(assignment.resource_display_name)
