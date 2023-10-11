"""
Retrieves site columns

"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
columns = client.sites.root.columns.get().execute_query()
for column in columns:  # type: ColumnDefinition
    print(column.name)
