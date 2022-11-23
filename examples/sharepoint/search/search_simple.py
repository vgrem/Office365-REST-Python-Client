from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_user_credentials

ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)
result = ctx.search.query("IsDocument:1").execute_query()
results = result.value.PrimaryQueryResult.RelevantResults
for row in results.Table.Rows:
    print(row.Cells["Path"])
