"""
Gets the range object specified by the address or name.

https://learn.microsoft.com/en-us/graph/api/worksheet-range?view=graph-rest-1.0
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

# worksheet_range = worksheets["Sheet1"].range().execute_query()
worksheet_range = worksheets["Sheet1"].range(address="A1:B3").execute_query()
print(worksheet_range.values)
