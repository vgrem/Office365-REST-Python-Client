"""
Demonstrates how to work with the Excel API

https://learn.microsoft.com/en-us/graph/api/resources/excel?view=graph-rest-1.0
"""
from examples.onedrive import ensure_workbook_sample
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
workbook = ensure_workbook_sample(client)

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
