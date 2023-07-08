"""

"""

from pprint import pprint

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_admin_site_url, test_tenant, test_client_id, test_cert_thumbprint, test_cert_path

admin_client = ClientContext(test_admin_site_url).with_client_certificate(test_tenant,
                                                                          client_id=test_client_id,
                                                                          thumbprint=test_cert_thumbprint,
                                                                          cert_path=test_cert_path)
tenant_details = Tenant(admin_client).get().execute_query()
pprint(tenant_details.properties)





