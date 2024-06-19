"""
Demonstrates how to work with the Excel API

https://learn.microsoft.com/en-us/graph/api/resources/excel?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)

local_path = "../../data/Financial Sample.xlsx"
excel_file = client.me.drive.root.upload_file(local_path).execute_query()
print("File {0} has been uploaded".format(excel_file.web_url))
workbook = excel_file.workbook

print("Creating a session...")
result = workbook.create_session().execute_query()

print("Reading a table...")
table = workbook.worksheets["Sheet1"].tables["financials"]
# read table content
rows = table.rows.get().execute_query()
for r in rows:
    print(r.values)

print("Refreshing a session...")
result_new = workbook.refresh_session(result.value.id).execute_query()

print("Closing a session...")
workbook.close_session(result.value.id).execute_query()
