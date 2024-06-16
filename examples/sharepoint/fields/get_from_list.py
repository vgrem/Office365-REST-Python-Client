"""
This example retrieves all fields in a SharePoint list.
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
target_list = client.web.lists.get_by_title("Site Pages")
fields = target_list.fields.get().execute_query()
for field in fields:
    print("Field name {0}".format(field.internal_name))
