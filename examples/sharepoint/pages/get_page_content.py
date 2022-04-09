from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from tests import test_client_credentials, test_site_url
ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)

file = ctx.web.get_file_by_server_relative_path("/SitePages/Home.aspx")  # type: File
file_item = file.listItemAllFields.select(["CanvasContent1"]).get().execute_query()
print(file_item.properties.get("CanvasContent1"))




