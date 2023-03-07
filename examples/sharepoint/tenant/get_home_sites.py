from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sites.home_sites_details import HomeSitesDetails
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_admin_site_url, test_client_credentials

admin_client = ClientContext(test_admin_site_url).with_credentials(test_client_credentials)
tenant = Tenant(admin_client)
result = tenant.get_home_sites().execute_query()
for details in result.value:  # type: HomeSitesDetails
    print(" {0}".format(details.Url))
