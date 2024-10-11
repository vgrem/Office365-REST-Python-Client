"""
Demonstrates how to retrieve deleted items (of File type)
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
result = (
    ctx.web.recycle_bin.get().execute_query()
)
for item in result:
    print(item.properties)
