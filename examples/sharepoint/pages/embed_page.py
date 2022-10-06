from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url
ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)

file_url = "/Shared Documents/Dummy.pdf"

file = ctx.web.get_file_by_server_relative_path(file_url).get().execute_query()
preview_url = "{0}/_layouts/15/embed.aspx?UniqueId={1}".format(ctx.base_url, file.unique_id)
print(preview_url)




