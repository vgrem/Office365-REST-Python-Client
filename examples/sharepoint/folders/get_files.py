from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
root_folder = ctx.web.default_document_library().root_folder
ctx.load(root_folder, ["Files"])
ctx.execute_query()
for file in root_folder.files:  # type: File
    print(file.name)
