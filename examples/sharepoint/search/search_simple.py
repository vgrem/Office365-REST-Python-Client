import json
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.search.search_service import SearchService
from tests import test_site_url, test_user_credentials

ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)
search = SearchService(ctx)
result = search.query("IsDocument:1").execute_query()
relevant_results = result.value.PrimaryQueryResult.RelevantResults
for i in relevant_results['Table']['Rows']:
    cells = relevant_results['Table']['Rows'][i]['Cells']
    print(json.dumps(cells, sort_keys=True, indent=4))
