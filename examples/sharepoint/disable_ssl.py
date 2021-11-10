from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.webs.web import Web
from tests import test_site_url, test_client_credentials

ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)


def disable_ssl(request):
    request.verify = False  # Disable certification verification


ctx.pending_request().beforeExecute += disable_ssl

web = ctx.web.get().execute_query()  # type: Web
print(web.url)
