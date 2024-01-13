"""
Demonstrates how to apply filtering to list collection

In the provided example only the user defined lists are getting returned
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
result = (
    ctx.web.lists.get_by_title("Site Pages")
    .items.filter("ID eq 135 AND RequestType eq 'Standard'")
    .get()
    .execute_query()
)
for item in result:
    print(item.properties)
