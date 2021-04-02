from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.site_properties import SiteProperties
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_admin_site_url, test_user_credentials

admin_client = ClientContext(test_admin_site_url).with_credentials(test_user_credentials)
tenant = Tenant(admin_client)
result = tenant.get_site_properties_from_sharepoint_by_filters("", 0).execute_query()
for siteProps in result:  # type: SiteProperties
    print(siteProps.url)
