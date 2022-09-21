import json

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.search.request import SearchRequest
from office365.sharepoint.search.service import SearchService
from tests import test_site_url, settings


def extract_cell_value(cells, name):
    """
    Extract cell value
    """
    return next((c.get("Value") for c in cells.values() if c.get("Key") == name), None)


user_credentials = UserCredential(settings.get('user_credentials', 'username'),
                                  settings.get('user_credentials', 'password'))
ctx = ClientContext(test_site_url).with_credentials(user_credentials)
search = SearchService(ctx)

request = SearchRequest(query_text="IsDocument:1", select_properties=["Title", "Path"],
                        trim_duplicates=False, row_limit=50)
result = search.post_query(request).execute_query()
relevant_results = result.value.PrimaryQueryResult.RelevantResults
for i in relevant_results['Table']['Rows']:
    cur_cells = relevant_results['Table']['Rows'][i]['Cells']
    file_url = extract_cell_value(cur_cells, "Path")
    print(file_url)
    # print(json.dumps(cells, sort_keys=True, indent=4))
