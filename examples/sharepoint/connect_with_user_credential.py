from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, settings

ctx = ClientContext(test_site_url)
ctx.with_user_credentials(settings.get('user_credentials', 'username'),
                          settings.get('user_credentials', 'password'))

web = ctx.web.get().execute_query()
print(web.url)
