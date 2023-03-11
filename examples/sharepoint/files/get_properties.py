import json

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_client_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = '/sites/team/Shared Documents/big_buck_bunny.mp4'
file = ctx.web.get_file_by_server_relative_url(file_url).get().execute_query()
#file = ctx.web.get_file_by_server_relative_url(file_url).expand(["ModifiedBy"]).get().execute_query()
#file = ctx.web.get_file_by_server_relative_url(file_url).expand(["ListItemAllFields"]).get().execute_query()

# print all file properties
#print(json.dumps(file.properties, indent=4))

# or directly via object properties
print("File size: ", file.length)
print("File name: ", file.name)
#print("File modified by: {0}".format(file.modified_by.properties.get('UserPrincipalName')))
#print("File modified by: {0}".format(file.listItemAllFields))
if file.properties.get('CheckOutType') == 0:
    print("The file is checked out for editing on the server")
elif file.properties.get('CheckOutType') == 1:
    print("The file is checked out for editing on the local computer.")
else:
    print("The file is not checked out.")



