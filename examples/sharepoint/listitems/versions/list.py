"""
Demonstrates how to retain the history for list items.
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
items = (
    ctx.web.lists.get_by_title("Site Pages")
    .items.get()
    .expand(["Versions"])
    .top(10)
    .execute_query()
)

for item in items:
    for version in item.versions:
        print(version)
