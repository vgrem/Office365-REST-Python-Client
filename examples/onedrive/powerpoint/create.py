from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient


client = GraphClient(acquire_token_by_username_password)

remote_drive = client.me.drive.root
pptx_file = remote_drive.create_powerpoint("sample.pptx").execute_query()
print(f"File {pptx_file.web_url} has been uploaded")
