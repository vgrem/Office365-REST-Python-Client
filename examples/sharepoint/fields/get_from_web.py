"""
This example demonstrates how to retrieve all fields in a SharePoint site.
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

web_fields = client.web.fields.get().execute_query()
for f in web_fields:
    print("Field name {0}".format(f.internal_name))
