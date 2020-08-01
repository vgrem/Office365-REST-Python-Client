from settings import settings

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.search.searchRequest import SearchRequest
from office365.sharepoint.search.searchService import SearchService

ctx = ClientContext.connect_with_credentials(settings['url'],
                                             UserCredential(settings['user_credentials']['username'],
                                                            settings['user_credentials']['password']))

search = SearchService(ctx)
request = SearchRequest("IsDocument:1")
result = search.post_query(request)
ctx.execute_query()
relevant_results = result.PrimaryQueryResult.RelevantResults
for i in relevant_results['Table']['Rows']:
    cells = relevant_results['Table']['Rows'][i]['Cells']
    print(cells[6]['Value'])
