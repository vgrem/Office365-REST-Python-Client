"""
Gets files within a folder
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
root_folder = ctx.web.default_document_library().root_folder
ctx.load(root_folder, ["Files"])
ctx.execute_query()
for file in root_folder.files:
    print(file.name)
