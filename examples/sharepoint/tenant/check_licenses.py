"""
Checks whether a tenant has the Intune license

"""
from office365.sharepoint.client_context import ClientContext
from tests import test_admin_site_url, test_admin_credentials

admin_client = ClientContext(test_admin_site_url).with_credentials(test_admin_credentials)
result = admin_client.tenant.check_tenant_intune_license().execute_query()
print(result.value)
