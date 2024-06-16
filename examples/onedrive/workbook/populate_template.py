"""
Demonstrates how to populate Excel template

https://learn.microsoft.com/en-us/graph/api/resources/excel?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)

local_path = "../../data/templates/Simple invoice that calculates total.xlsx"
excel_file = client.me.drive.root.upload_file(local_path).execute_query()
