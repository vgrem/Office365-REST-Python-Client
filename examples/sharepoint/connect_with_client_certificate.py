import os
from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_tenant

cert_settings = {
    'client_id': '51d03106-4726-442c-86db-70b32fa7547f',
    'thumbprint': "6B36FBFC86FB1C019EB6496494B9195E6D179DDB",
    'certificate_path': '{0}/selfsigncert.pem'.format(os.path.dirname(__file__))
}

ctx = ClientContext(test_site_url).with_client_certificate(test_tenant,
                                                           cert_settings.get('client_id'),
                                                           cert_settings.get('thumbprint'),
                                                           cert_settings.get('certificate_path'))
current_web = ctx.web.get().execute_query()
print("{0}".format(current_web.url))
