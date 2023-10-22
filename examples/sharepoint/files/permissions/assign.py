"""
The example demonstrates how to assign a custom permissions on a file
"""
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.role_type import RoleType
from tests import (
    test_client_credentials,
    test_team_site_url,
    test_user_principal_name_alt,
)

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "Shared Documents/report #123.csv"

# Step 1: retrieve objects
role_def = client.web.role_definitions.get_by_type(
    RoleType.Contributor
)  # address role by type
user = client.web.site_users.get_by_email(
    test_user_principal_name_alt
)  # address user by email
target_file = client.web.get_file_by_server_relative_path(
    file_url
)  # address file by relative url

# Step 2: to assign a custom permissions to a file
target_file.listItemAllFields.add_role_assignment(user, role_def).execute_query()
