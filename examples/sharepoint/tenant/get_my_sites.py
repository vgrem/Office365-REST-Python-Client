from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.sites.properties import SiteProperties
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_admin_site_url, test_user_principal_name, test_admin_credentials

admin_client = ClientContext(test_admin_site_url).with_credentials(test_admin_credentials)
tenant = Tenant(admin_client)
result = tenant.get_site_properties_from_sharepoint_by_filters("").execute_query()

def try_get_user_permissions(site_url, user_name):
    ctx = ClientContext(site_url).with_credentials(test_admin_credentials)
    try:
        perms_result = ctx.web.get_user_effective_permissions(user_name).execute_query()
        #todo: determine user permissions from result
        return True
    except ClientRequestException as e:
        if e.response.status_code == 404:
            return False
        else:
            raise ValueError(e.response.text)


for siteProps in result:  # type: SiteProperties
    print("Current site url: {0}".format(siteProps.url))
    if try_get_user_permissions(siteProps.url, test_user_principal_name) is True:
        print("Site url {0} {1} user has access to".format(siteProps.url, test_user_principal_name))
