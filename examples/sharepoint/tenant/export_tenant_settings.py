from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_admin_site_url, test_client_credentials

admin_client = ClientContext(test_admin_site_url).with_credentials(test_client_credentials)
result = Tenant(admin_client).export_to_csv().execute_query()
print("Sites details have been exported into {0}{1}".format(test_admin_site_url, result.value))





