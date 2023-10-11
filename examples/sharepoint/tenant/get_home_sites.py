from office365.sharepoint.client_context import ClientContext
from tests import test_admin_credentials, test_admin_site_url

admin_client = ClientContext(test_admin_site_url).with_credentials(
    test_admin_credentials
)
result = admin_client.tenant.get_home_sites().execute_query()
for details in result.value:
    print(" {0}".format(details.Url))
