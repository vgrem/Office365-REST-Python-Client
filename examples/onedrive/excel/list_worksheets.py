"""
Retrieve a list of worksheet objects.

https://learn.microsoft.com/en-us/graph/api/workbook-list-worksheets?view=graph-rest-1.0
"""

import sys

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
drive_item = client.me.drive.root.get_by_path("Financial Sample.xlsx")
worksheets = drive_item.workbook.worksheets.get().execute_query()
if len(worksheets) == 0:
    sys.exit("No worksheets found")

for worksheet in worksheets:
    print("Worksheet name: {0}".format(worksheet))
