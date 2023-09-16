import sys

from examples.onedrive import upload_excel_sample
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
drive_item = upload_excel_sample(client)
# Load worksheets
worksheets = drive_item.workbook.worksheets.get().execute_query()
if len(worksheets) == 0:
    sys.exit("No worksheets found")
print("Worksheet name: {0}".format(worksheets[0].name))
