from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.search.query.sort.sort import Sort
from tests import test_site_url, test_user_credentials

ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)
result = ctx.search.post_query(query_text="IsDocument:1",
                               sort_list=[Sort("LastModifiedTime", 1)],
                               select_properties=["Path", "LastModifiedTime"],
                               row_limit=20).execute_query()
results = result.value.PrimaryQueryResult.RelevantResults
for row in results.Table.Rows:
    print(row.Cells["Path"], row.Cells["LastModifiedTime"])
