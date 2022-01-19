import os
from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_tenant

cert_settings = {
    'client_id': '51d03106-4726-442c-86db-70b32fa7547f',
    'thumbprint': "61C754D8D9629BE91972B6A0C1999DC678FB0145",
    'cert_path': '{0}/selfsigncert.pem'.format(os.path.dirname(__file__))
}

ctx = ClientContext(test_site_url).with_client_certificate(test_tenant, **cert_settings)
current_web = ctx.web.get().execute_query()
print("{0}".format(current_web.url))
