"""
Demonstrates how to copy a folder using path
"""

from office365.sharepoint.client_context import ClientContext
from tests import create_unique_name, test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

# creates a temporary folder first in a Documents library
folder_from = ctx.web.default_document_library().root_folder.add(
    create_unique_name("from")
)


# folder_to = ctx.web.default_document_library().root_folder.add(create_unique_name("to"))
folder_to_url = "Shared Documents/Archive/2001/01"

# copies the folder with a new name
folder = folder_from.copy_to_using_path(folder_to_url).execute_query()
print(
    "Folder has been copied from '{0}' into '{1}'".format(
        folder_from.server_relative_path, folder.server_relative_path
    )
)

# clean up
folder_from.delete_object().execute_query()
folder.delete_object().execute_query()
