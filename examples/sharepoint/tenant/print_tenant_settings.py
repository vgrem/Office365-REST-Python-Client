import os
from pprint import pprint

from examples import sample_cert_path, sample_thumbprint, sample_client_id
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_admin_site_url, test_tenant


admin_client = ClientContext(test_admin_site_url).with_client_certificate(test_tenant,
                                                                          client_id=sample_client_id,
                                                                          thumbprint=sample_thumbprint,
                                                                          cert_path=sample_cert_path)
tenant_details = Tenant(admin_client).get().execute_query()
pprint(tenant_details.properties)





