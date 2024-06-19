"""
Reads table rows

https://learn.microsoft.com/en-us/graph/api/resources/excel?view=graph-rest-1.0#get-list-of-table-rows
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
drive_item = client.me.drive.root.get_by_path("Financial Sample.xlsx")
table = (
    drive_item.workbook.worksheets["Sheet1"].tables["financials"].get().execute_query()
)
print(table.name)

# read table content
rows = table.rows.get().execute_query()
for r in rows:
    print(r.values)
