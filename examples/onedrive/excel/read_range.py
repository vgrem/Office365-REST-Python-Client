"""
Gets the range object specified by the address or name.

https://learn.microsoft.com/en-us/graph/api/worksheet-range?view=graph-rest-1.0
"""

import sys

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
drive_item = client.me.drive.root.get_by_path("Financial Sample.xlsx")
worksheets = drive_item.workbook.worksheets.get().execute_query()
if len(worksheets) == 0:
    sys.exit("No worksheets found")

# worksheet_range = worksheets["Sheet1"].range().execute_query()
worksheet_range = worksheets["Sheet1"].range(address="A2:P10").execute_query()
print(worksheet_range)
