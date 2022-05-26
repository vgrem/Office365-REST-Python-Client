import json

from office365.runtime.types.string_collection import StringCollection
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.search.query.sort import Sort
from office365.sharepoint.search.search_request import SearchRequest
from office365.sharepoint.search.search_service import SearchService
from tests import test_site_url, test_user_credentials

ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)
search = SearchService(ctx)

select_props = StringCollection(["Path", "LastModifiedTime"])
request = SearchRequest("IsDocument:1", SelectProperties=select_props)
request.SortList.add(Sort("ModifiedBy", 1))
result = search.post_query(request).execute_query()
relevant_results = result.value.PrimaryQueryResult.RelevantResults
