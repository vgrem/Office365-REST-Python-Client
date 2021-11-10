from pprint import pprint

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_admin_site_url, test_user_credentials

admin_client = ClientContext(test_admin_site_url).with_credentials(test_user_credentials)
tenant = Tenant(admin_client)
tenant.get().execute_query()
pprint(tenant.properties)





