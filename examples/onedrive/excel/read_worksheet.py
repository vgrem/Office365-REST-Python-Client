import sys

from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient


def upload_sample(graph_client):
    """
    :type graph_client: GraphClient
    """
    local_path = "../../data/Financial Sample.xlsx"
    target_file = graph_client.me.drive.root.resumable_upload(local_path).execute_query()
    print(f"File {target_file.web_url} has been uploaded")


file_name = "Financial Sample.xlsx"
client = GraphClient(acquire_token_by_username_password)
# upload_sample(client)

# Load worksheets
worksheets = client.me.drive.root.get_by_path(file_name).workbook.worksheets.get().execute_query()
if len(worksheets) == 0:
    sys.exit("No worksheets found")
print("Worksheet name: {0}".format(worksheets[0].name))
