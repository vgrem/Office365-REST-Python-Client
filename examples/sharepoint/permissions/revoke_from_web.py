"""
Revokes user access from web
"""
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.role_type import RoleType
from tests import (
    test_client_credentials,
    test_team_site_url,
    test_user_principal_name_alt,
)

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
result = ctx.web.remove_role_assignment(
    test_user_principal_name_alt, RoleType.Contributor
).execute_query()
print("Access has been revoked")
