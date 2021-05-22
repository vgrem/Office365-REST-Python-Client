import json

from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.search.searchRequest import SearchRequest
from office365.sharepoint.search.searchService import SearchService
from tests import test_site_url, test_user_credentials

ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)
search = SearchService(ctx)

select_props = ClientValueCollection(str, ["Title", "Path"])
request = SearchRequest("IsDocument:1", SelectProperties=select_props, TrimDuplicates=False, RowLimit=500)
result = search.post_query(request).execute_query()
relevant_results = result.value.PrimaryQueryResult.RelevantResults
for i in relevant_results['Table']['Rows']:
    cells = relevant_results['Table']['Rows'][i]['Cells']
    print(json.dumps(cells, sort_keys=True, indent=4))
