from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.role_type import RoleType
from tests import test_team_site_url, test_client_credentials, test_user_principal_name_alt

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "/sites/team/Shared Documents/report #123.csv"

# get Contributor role
role_def = client.web.role_definitions.get_by_type(RoleType.Contributor)

# get user by email
user = client.web.site_users.get_by_email(test_user_principal_name_alt)

# assign user with role to file
target_file = client.web.get_file_by_server_relative_path(file_url)
target_file.listItemAllFields.add_role_assignment(user, role_def).execute_query()
