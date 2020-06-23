from settings import settings

from office365.runtime.auth.clientCredential import ClientCredential
from office365.sharepoint.client_context import ClientContext

credentials = ClientCredential(settings['client_credentials']['client_id'],
                               settings['client_credentials']['client_secret'])
ctx = ClientContext(settings['url']).with_credentials(credentials)
if not ctx.authentication_context.acquire_token():
    print("Acquire token failed")


target_web = ctx.web
ctx.load(target_web)
ctx.execute_query()
print(target_web.url)
