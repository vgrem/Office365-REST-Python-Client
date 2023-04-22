from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_user_credentials

ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)
result = ctx.search.query("IsDocument:1", row_limit=10).execute_query()
for row in result.value.PrimaryQueryResult.RelevantResults.Table.Rows:
    print(row.Cells["Path"])

print("Next query..")

result = ctx.search.query("IsDocument:0", row_limit=5).execute_query()
for row in result.value.PrimaryQueryResult.RelevantResults.Table.Rows:
    print(row.Cells["Path"])
