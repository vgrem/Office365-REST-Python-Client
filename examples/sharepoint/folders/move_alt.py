"""
Demonstrates how to move a folder within a site
"""
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.utilities.move_copy_options import MoveCopyOptions
from office365.sharepoint.utilities.move_copy_util import MoveCopyUtil
from tests import create_unique_name, test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)


print("Creating a temporary folders in a Documents library ...")
folder_from = (
    ctx.web.default_document_library()
    .root_folder.add(create_unique_name("in"))
    .execute_query()
)
path = "../../data/report.csv"
folder_from.files.upload(path).execute_query()
folder_to_url = "Shared Documents/{0}".format(create_unique_name("out"))

print("Moving folder...")
opt = MoveCopyOptions()
MoveCopyUtil.move_folder(
    ctx, folder_from.serverRelativeUrl, folder_to_url, opt
).execute_query()
print("Folder has been moved into '{0}'".format(folder_to_url))

print("Cleaning up temporary resources ...")
folder_to = ctx.web.get_folder_by_server_relative_url(folder_to_url)
folder_to.delete_object().execute_query()
print("Done")
