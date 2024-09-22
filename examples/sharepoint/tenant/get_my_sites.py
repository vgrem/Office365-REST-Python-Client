"""
Gets my sites
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_user_credentials

client = ClientContext(test_site_url).with_credentials(test_user_credentials)

result = client.search.query("contentclass:STS_Site").execute_query()
results = result.value.PrimaryQueryResult.RelevantResults
for row in results.Table.Rows:
    site_url = row.Cells["Path"]
    print(site_url)
