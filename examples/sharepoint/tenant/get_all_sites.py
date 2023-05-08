from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.sites.properties import SiteProperties
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_admin_site_url, test_client_credentials

admin_client = ClientContext(test_admin_site_url).with_credentials(test_client_credentials)
tenant = Tenant(admin_client)
result = tenant.get_site_properties_from_sharepoint_by_filters("").execute_query()
for i, siteProps in enumerate(result):  # type: SiteProperties
    print("({0} of {1}) {2}".format(i, len(result), siteProps.url))
