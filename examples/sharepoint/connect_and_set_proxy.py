from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.webs.web import Web
from tests import test_site_url, test_client_id, test_client_secret


def set_proxy(request):
    print("Inject proxy settings...")
    #proxies = {settings.get('default', 'site_url'): 'https://127.0.0.1:8888'}
    #request.proxies = proxies


ctx = ClientContext(test_site_url).with_client_credentials(test_client_id, test_client_secret)

ctx.pending_request().beforeExecute += set_proxy

result = Web.get_context_web_information(ctx).execute_query()
print(result.value.LibraryVersion)
