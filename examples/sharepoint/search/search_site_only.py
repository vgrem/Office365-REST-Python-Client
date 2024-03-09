"""
Search for document files within a specific site
Path managed property is provided to limit search scope

https://learn.microsoft.com/en-us/sharepoint/dev/general-development/sharepoint-search-rest-api-overview
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_team_site_url, test_user_credentials

ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)

result = ctx.search.post_query(
    "Path={0}/*".format(test_team_site_url), row_limit=10
).execute_query()
for row in result.value.PrimaryQueryResult.RelevantResults.Table.Rows:
    print("{0}".format(row.Cells["Path"]))
