"""
Creates a PowerPoint file
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
remote_drive = client.me.drive.root
pptx_file = remote_drive.create_powerpoint("sample.pptx").execute_query()
print(f"File {pptx_file.web_url} has been uploaded")
