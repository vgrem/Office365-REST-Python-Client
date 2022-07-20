from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url

ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
folder_path = "Shared Documents/archive/2020/12"
ctx.web.get_folder_by_server_relative_path(folder_path).delete_object().execute_query()
