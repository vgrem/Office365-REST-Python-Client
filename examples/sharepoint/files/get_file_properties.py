from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = '/sites/team/Shared Documents/big_buck_bunny.mp4'
remote_file = ctx.web.get_file_by_server_relative_url(file_url)

remote_file.get()
ctx.execute_query()
print("All file properties")
for key, val in remote_file.properties.items():
    print("{}:\t{}".format(key, val))

# or via direct object properties
print("file size: ", remote_file.length)
print("file name: ", remote_file.name)
