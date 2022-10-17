from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_client_credentials, test_admin_site_url

admin_client = ClientContext(test_admin_site_url).with_credentials(test_client_credentials)
tenant = Tenant(admin_client)
result = tenant.render_recent_admin_actions().execute_query()
print(result)
