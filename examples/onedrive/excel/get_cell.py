"""
Gets the range object containing the single cell based on row and column numbers.

https://learn.microsoft.com/en-us/graph/api/worksheet-cell?view=graph-rest-1.0
"""
import sys

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
drive_item = client.me.drive.root.get_by_path("Financial Sample.xlsx")
worksheets = drive_item.workbook.worksheets.get().execute_query()
if len(worksheets) == 0:
    sys.exit("No worksheets found")


result = worksheets["Sheet1"].cell(row=1, column=1).execute_query()
print(result.values)
