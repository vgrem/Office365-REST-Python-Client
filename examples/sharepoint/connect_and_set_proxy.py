from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.webs.web import Web
from tests import load_settings

settings = load_settings()


def set_proxy(request):
    print("Inject proxy settings...")
    #proxies = {settings.get('default', 'site_url'): 'https://127.0.0.1:8888'}
    #request.proxies = proxies


ctx = ClientContext(settings.get('default', 'site_url'))\
    .with_credentials(ClientCredential(settings.get('client_credentials', 'client_id'),
                                       settings.get('client_credentials', 'client_secret')))

ctx.pending_request().beforeExecute += set_proxy

# web = ctx.web.get().execute_query()
# print(web.url)

result = Web.get_context_web_information(ctx).execute_query()
print(result.value.LibraryVersion)
