"""
Reads table rows

https://learn.microsoft.com/en-us/graph/api/resources/excel?view=graph-rest-1.0#get-list-of-table-rows
"""
from examples.onedrive import upload_excel_sample
from office365.graph_client import GraphClient
from office365.onedrive.workbooks.tables.rows.row import WorkbookTableRow
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
drive_item = upload_excel_sample(client)
table = (
    drive_item.workbook.worksheets["Sheet1"].tables["financials"].get().execute_query()
)
print(table.name)

# read table content
rows = table.rows.get().execute_query()
for r in rows:  # type: WorkbookTableRow
    print(r.values)
