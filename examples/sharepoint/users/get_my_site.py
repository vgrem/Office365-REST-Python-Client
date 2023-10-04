"""
Gets personal site for a user

"""
from office365.sharepoint.client_context import ClientContext
from tests import test_password, test_site_url, test_username

ctx = ClientContext(test_site_url).with_user_credentials(test_username, test_password)
my_site = ctx.web.current_user.get_personal_site().execute_query()
print(my_site.url)
