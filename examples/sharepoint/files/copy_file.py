"""
Demonstrates how to copy a folder within a site
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_user_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

# uploads a temporary folder first in a Documents library
path = "../../data/report #123.csv"
file_from = ctx.web.default_document_library().root_folder.files.upload(path).execute_query()

# copies the file with a new name into folder
new_file_name = "report copied.csv"
file_to = file_from.copyto_using_path(new_file_name, True).execute_query()
print("Folder has been copied into '{0}'".format(file_to.server_relative_path))

# clean up
file_from.delete_object().execute_query()
file_to.delete_object().execute_query()
