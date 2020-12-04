from settings import settings

from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext

credentials = ClientCredential(settings.get('client_credentials').get('client_id'),
                               settings.get('client_credentials').get('client_secret'))
ctx = ClientContext(settings['url']).with_credentials(credentials)
target_web = ctx.web.get().execute_query()
print(target_web.url)
