"""
Retrieves file extended properties (accessible via associated ListItem)
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "SitePages/Home.aspx"
file_item = (
    ctx.web.get_file_by_server_relative_url(file_url)
    .listItemAllFields.get()
    .execute_query()
)
for k, v in file_item.properties.items():
    print("{0}: {1}".format(k, v))
