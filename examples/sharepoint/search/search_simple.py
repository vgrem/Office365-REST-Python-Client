"""
Search for document files in tenant

https://learn.microsoft.com/en-us/sharepoint/dev/general-development/sharepoint-search-rest-api-overview
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_user_credentials

ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)
result = ctx.search.query("IsDocument:1", row_limit=10).execute_query()
for i, row in enumerate(result.value.PrimaryQueryResult.RelevantResults.Table.Rows):
    print("{0}: {1}".format(i + 1, row.Cells["Path"]))
