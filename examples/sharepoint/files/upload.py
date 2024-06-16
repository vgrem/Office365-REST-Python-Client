"""
Demonstrates how to upload a small files (up to 4MB in size)
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

list_title = "Documents"
folder = ctx.web.lists.get_by_title(list_title).root_folder
path = "../../data/Financial Sample.xlsx"
with open(path, "rb") as f:
    file = folder.files.upload(f).execute_query()
print("File has been uploaded into: {0}".format(file.serverRelativeUrl))
