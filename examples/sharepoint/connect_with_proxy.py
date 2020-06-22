from settings import settings

from office365.runtime.auth.clientCredential import ClientCredential
from office365.sharepoint.client_context import ClientContext


def set_proxy(request):
    proxies = {settings['url']: 'https://127.0.0.1:8888'}
    request.proxies = proxies


ctx = ClientContext.connect_with_credentials(settings['url'],
                                             ClientCredential(settings['client_credentials']['client_id'],
                                                              settings['client_credentials']['client_secret']))

ctx.get_pending_request().beforeExecute += set_proxy

target_web = ctx.web
ctx.load(target_web)
ctx.execute_query()
