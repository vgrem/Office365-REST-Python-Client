"""

"""
import os

from office365.sharepoint.client_context import ClientContext
from tests import test_tenant_name, test_client_id, test_cert_thumbprint, test_site_url

cert_credentials = {
    'tenant': test_tenant_name,
    'client_id': test_client_id,
    'thumbprint': test_cert_thumbprint,
    'cert_path': '{0}/selfsigncert.pem'.format(os.path.dirname(__file__)),
    'scopes': ['{0}/.default'.format(test_site_url)]
}

ctx = ClientContext(test_site_url).with_client_certificate(**cert_credentials)
current_web = ctx.web.get().execute_query()
print("{0}".format(current_web.url))
