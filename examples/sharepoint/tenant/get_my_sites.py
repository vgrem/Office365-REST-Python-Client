from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_admin_credentials, test_admin_site_url, test_user_principal_name

admin_client = ClientContext(test_admin_site_url).with_credentials(
    test_admin_credentials
)
tenant = Tenant(admin_client)
result = tenant.get_site_properties_from_sharepoint_by_filters("").execute_query()


def try_get_user_permissions(site_url, user_name):
    ctx = ClientContext(site_url).with_credentials(test_admin_credentials)
    try:
        ctx.web.get_user_effective_permissions(user_name).execute_query()
        # todo: determine user permissions from result
        return True
    except ClientRequestException as e:
        if e.response.status_code == 404:
            return False
        else:
            raise ValueError(e.response.text)


for siteProps in result:
    print("Current site url: {0}".format(siteProps.url))
    if try_get_user_permissions(siteProps.url, test_user_principal_name) is True:
        print(
            "Site url {0} {1} user has access to".format(
                siteProps.url, test_user_principal_name
            )
        )
