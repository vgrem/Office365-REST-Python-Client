import os
from pprint import pprint

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_admin_site_url, test_tenant

cert_settings = {
    'client_id': '51d03106-4726-442c-86db-70b32fa7547f',
    'thumbprint': "61C754D8D9629BE91972B6A0C1999DC678FB0145",
    'cert_path': '{0}/../selfsigncert.pem'.format(os.path.dirname(__file__))
}

admin_client = ClientContext(test_admin_site_url).with_client_certificate(test_tenant, **cert_settings)
tenant_details = Tenant(admin_client).get().execute_query()
pprint(tenant_details.properties)





