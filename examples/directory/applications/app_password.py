"""
Adds a strong password or secret to an application.
https://learn.microsoft.com/en-us/graph/api/application-addpassword?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests import test_client_credentials
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
target_app = client.applications.get_by_app_id(test_client_credentials.clientId)
result = target_app.add_password("Password friendly name").execute_query()
print(result.value)
