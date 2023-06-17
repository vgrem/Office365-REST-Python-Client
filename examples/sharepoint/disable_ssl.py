from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_client_credentials

import ssl

print(ssl.OPENSSL_VERSION)


def disable_ssl(request):
    print("Disabling certification verification...")
    request.verify = False  # Disable certification verification


ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
ctx.pending_request().beforeExecute += disable_ssl
web = ctx.web.get().execute_query()
print(web.url)
