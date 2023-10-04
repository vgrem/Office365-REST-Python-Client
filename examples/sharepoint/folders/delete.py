"""
Demonstrates how to delete a folder
"""
from office365.sharepoint.client_context import ClientContext
from tests import create_unique_name, test_client_credentials, test_site_url

ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)

folder_name = create_unique_name(
    "Temp folder"
)  # creates a temporary folder first in Documents library
folder = ctx.web.default_document_library().root_folder.add(folder_name)
folder.delete_object().execute_query()
print("Folder has been deleted")
