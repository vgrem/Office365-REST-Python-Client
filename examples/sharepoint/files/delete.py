"""
Deletes a file from SharePoint site
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
file_url = "Shared Documents/Financial Sample.xlsx"
file = ctx.web.get_file_by_server_relative_url(file_url)
# file.recycle().execute_query()
# or delete permanently via delete_object:
# file.delete_object().execute_query()
print("Deleted file: {0}".format(file_url))


print("Print deleted files...")
result = ctx.web.get_recycle_bin_items().execute_query()
for recycle_bin_item in result:
    print(recycle_bin_item)
