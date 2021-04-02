from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from tests import load_settings

settings = load_settings()


def set_proxy(request):
    proxies = {settings.get('default', 'site_url'): 'https://127.0.0.1:8888'}
    request.proxies = proxies


ctx = ClientContext(settings.get('default', 'site_url'))\
    .with_credentials(ClientCredential(settings.get('client_credentials', 'client_id'),
                                       settings.get('client_credentials', 'client_secret')))

ctx.pending_request().beforeExecute += set_proxy

target_web = ctx.web
ctx.load(target_web)
ctx.execute_query()
