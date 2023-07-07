"""
Demonstrates how to work with the Excel API

https://learn.microsoft.com/en-us/graph/api/resources/excel?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from office365.onedrive.workbooks.tables.rows.row import WorkbookTableRow
from office365.runtime.client_request_exception import ClientRequestException
from tests.graph_case import acquire_token_by_username_password


def ensure_workbook_sample(graph_client):
    """
    :type graph_client: GraphClient
    """
    try:
        return graph_client.me.drive.root.get_by_path("Financial Sample.xlsx").workbook.get().execute_query()
    except ClientRequestException as e:
        if e.response.status_code == 404:
            local_path = "../../data/Financial Sample.xlsx"
            target_file = graph_client.me.drive.root.upload(local_path).execute_query()
            print(f"File {target_file.web_url} has been uploaded")
            return target_file.workbook
        else:
            raise ValueError(e.response.text)


client = GraphClient(acquire_token_by_username_password)
workbook = ensure_workbook_sample(client)

print("Creating a session...")
result = workbook.create_session().execute_query()

print("Reading a table...")
table = workbook.worksheets["Sheet1"].tables["financials"]
# read table content
rows = table.rows.get().execute_query()
for r in rows:  # type: WorkbookTableRow
    print(r.values)

print("Refreshing a session...")
result_new = workbook.refresh_session(result.value.id).execute_query()

print("Closing a session...")
workbook.close_session(result.value.id).execute_query()
