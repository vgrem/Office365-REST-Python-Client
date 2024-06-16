"""
Get personal site for current user
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
my_site = ctx.web.current_user.get_personal_site().execute_query()
print(my_site.url)
