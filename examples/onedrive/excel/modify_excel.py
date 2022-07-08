from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

file_name = "Financial Sample.xlsx"
client = GraphClient(acquire_token_by_username_password)
excel_file = client.me.drive.root.get_by_path(file_name).get().execute_query()
print(excel_file.name)

