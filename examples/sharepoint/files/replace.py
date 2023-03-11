import os

from office365.sharepoint.client_context import ClientContext
from tests import test_user_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

path = "../../data/report #123.csv"
with open(path, 'rb') as content_file:
    file_content = content_file.read()

target_folder = ctx.web.get_folder_by_server_relative_path("/sites/team/Shared Documents")
name = os.path.basename(path)
target_file = target_folder.upload_file(name, file_content).execute_query()
print("File has been uploaded to url: {0}".format(target_file.serverRelativeUrl))
