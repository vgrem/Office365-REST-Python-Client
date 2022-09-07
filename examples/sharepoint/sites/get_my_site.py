from office365.sharepoint.client_context import ClientContext
from tests import test_user_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
my_site = ctx.web.current_user.get_personal_site().execute_query()
print(my_site.url)
