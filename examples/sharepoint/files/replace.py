"""
Demonstrates how to replace file content
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_user_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

path = "../../data/report #123.csv"

print("Uploading a new file...")
with open(path, 'rb') as f:
    target_file = ctx.web.default_document_library().root_folder.files.upload(f).execute_query()


print("Replacing file content...")
with open(path, 'rb') as content_file:
    file_content = content_file.read()
target_file.save_binary_stream(file_content).execute_query()

print("Cleaning up resources...")
target_file.delete_object().execute_query()
