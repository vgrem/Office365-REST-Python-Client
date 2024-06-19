"""
Expands group to a collection of principals.
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_id, test_client_secret, test_team_site_url

ctx = ClientContext(test_team_site_url).with_client_credentials(
    test_client_id, test_client_secret
)

result = ctx.web.associated_member_group.expand_to_principals(100).execute_query()
for principal_info in result.value:
    print(principal_info)
