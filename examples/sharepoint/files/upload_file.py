import os

from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_user_credentials

ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)

path = "../../../tests/data/SharePoint User Guide.docx"
with open(path, 'rb') as content_file:
    file_content = content_file.read()

list_title = "Documents"
target_folder = ctx.web.lists.get_by_title(list_title).root_folder
name = os.path.basename(path)
target_file = target_folder.upload_file(name, file_content)
ctx.execute_query()
print("File has been uploaded to url: {0}".format(target_file.serverRelativeUrl))
