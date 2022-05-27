from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.search.query.sort import Sort
from office365.sharepoint.search.search_request import SearchRequest
from office365.sharepoint.search.search_service import SearchService
from tests import test_site_url, test_user_credentials

ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)
search = SearchService(ctx)

request = SearchRequest(query_text="IsDocument:1",
                        sort_list=[Sort("LastModifiedTime", 1)],
                        select_properties=["Path", "LastModifiedTime"],
                        row_limit=20)
result = search.post_query(request).execute_query()
relevant_results = result.value.PrimaryQueryResult.RelevantResults
for r in relevant_results.get('Table').get('Rows').items():
    cells = r[1].get('Cells')
    print(cells[1].get('Value'))
