"""
Export personal data

https://learn.microsoft.com/en-us/graph/api/user-exportpersonaldata?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
result = client.me.export_personal_data("storageLocation-value").execute_query()
