from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.site_properties import SiteProperties
from office365.sharepoint.tenant.administration.tenant import Tenant
from settings import settings

credentials = UserCredential(settings['user_credentials']['username'],
                             settings['user_credentials']['password'])

admin_client = ClientContext(settings.get("admin_site_url")).with_credentials(credentials)
tenant = Tenant(admin_client)
result = tenant.get_site_properties_from_sharepoint_by_filters("", 0).execute_query()
for siteProps in result:  # type: SiteProperties
    print(siteProps.get_property('Url'))
