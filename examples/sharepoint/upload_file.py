import os
from office365.runtime.auth.UserCredential import UserCredential
from settings import settings
from office365.sharepoint.client_context import ClientContext


ctx = ClientContext.connect_with_credentials(settings['url'],
                                             UserCredential(settings['user_credentials']['username'],
                                                            settings['user_credentials']['password']))

path = "../../tests/data/SharePoint User Guide.docx"
with open(path, 'rb') as content_file:
    file_content = content_file.read()

list_title = "Documents"
target_folder = ctx.web.lists.get_by_title(list_title).rootFolder
name = os.path.basename(path)
target_file = target_folder.upload_file(name, file_content)
ctx.execute_query()
print("File url: {0}".format(target_file.serverRelativeUrl))
