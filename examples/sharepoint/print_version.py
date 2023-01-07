from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.webs.web import Web
from tests import test_site_url, test_client_credentials


ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
result = Web.get_context_web_information(ctx).execute_query()
print(result.value.LibraryVersion)
