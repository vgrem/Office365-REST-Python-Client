import json

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = '/sites/team/Shared Documents/big_buck_bunny.mp4'
file = ctx.web.get_file_by_server_relative_url(file_url).get().execute_query()

# print all file properties
print(json.dumps(file.properties))

# or via direct object properties
print("file size: ", file.length)
print("file name: ", file.name)
