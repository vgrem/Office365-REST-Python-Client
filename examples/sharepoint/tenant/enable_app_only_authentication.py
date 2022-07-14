"""
Since for new tenants, apps using an ACS app-only access token is disabled by default,
you can change the behavior using the below script
"""


from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_admin_site_url, test_user_credentials

admin_client = ClientContext(test_admin_site_url).with_credentials(test_user_credentials)
tenant = Tenant(admin_client).get().execute_query()
# print(tenant.get_property("DisableCustomAppAuthentication"))
if tenant.get_property("DisableCustomAppAuthentication"):
    tenant.set_property("DisableCustomAppAuthentication", False).update().execute_query()





