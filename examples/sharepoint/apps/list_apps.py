from office365.sharepoint.client_context import ClientContext
from tests import test_admin_credentials, test_admin_site_url

admin_client = ClientContext(test_admin_site_url).with_credentials(
    test_admin_credentials
)
apps = admin_client.web.tenant_app_catalog.available_apps.get().execute_query()
for app in apps:  # type: CorporateCatalogAppMetadata
    print(app.title)
