from office365.graph_client import GraphClient
from office365.onedrive.workbooks.tables.rows.row import WorkbookTableRow
from tests.graph_case import acquire_token_by_username_password

file_name = "Financial Sample.xlsx"
client = GraphClient(acquire_token_by_username_password)
workbook = client.me.drive.root.get_by_path(file_name).workbook
table = workbook.worksheets["Sheet1"].tables["financials"].get().execute_query()
print(table.name)

# read table content
rows = table.rows.get().execute_query()
for r in rows:  # type: WorkbookTableRow
    print(r.values)
