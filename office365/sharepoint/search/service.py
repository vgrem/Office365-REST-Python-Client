from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.compat import is_string_type
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.search.query.auto_completion_results import QueryAutoCompletionResults
from office365.sharepoint.search.query.popular_tenant_query import PopularTenantQuery
from office365.sharepoint.search.query.suggestion_results import QuerySuggestionResults
from office365.sharepoint.search.query.tenantCustomQuerySuggestions import TenantCustomQuerySuggestions
from office365.sharepoint.search.request import SearchRequest
from office365.sharepoint.search.result import SearchResult


class SearchService(BaseEntity):
    """SearchService exposes OData Service Operations."""

    def __init__(self, context):
        super(SearchService, self).__init__(context, ResourcePath("Microsoft.Office.Server.Search.REST.SearchService"))

    def export(self, user_name, start_time):
        """
        The operation is used by the administrator to retrieve the query log entries,
        issued after a specified date, for a specified user.

        :param datetime.datetime start_time: The timestamp of the oldest query log entry returned.
        :param str user_name: The name of the user that issued the queries."""
        result = ClientResult(self.context)
        payload = {
            "userName": user_name,
            "startTime": start_time.isoformat()
        }
        qry = ServiceOperationQuery(self, "export", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def export_manual_suggestions(self):
        return_type = ClientResult(self.context, TenantCustomQuerySuggestions())
        qry = ServiceOperationQuery(self, "exportmanualsuggestions", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def export_popular_tenant_queries(self, count):
        """This method is used to get a list of popular search queries executed on the tenant.
        """
        return_type = ClientResult(self.context, ClientValueCollection(PopularTenantQuery))
        payload = {
            "count": count,
        }
        qry = ServiceOperationQuery(self, "exportpopulartenantqueries", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def query(self, request_or_query):
        """The operation is used to retrieve search results by using the HTTP protocol with the GET method.

        :type request_or_query: office365.sharepoint.search.request.SearchRequest or str
        """
        if is_string_type(request_or_query):
            params = SearchRequest(query_text=request_or_query)
        else:
            params = request_or_query
        result = ClientResult(self.context, SearchResult())
        qry = ServiceOperationQuery(self, "query", params.to_json(), None, "query", result)
        self.context.add_query(qry)

        def _construct_request(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            request.method = HttpMethod.Get

        self.context.before_execute(_construct_request)
        return result

    def post_query(self, query_text, select_properties=None, trim_duplicates=None, row_limit=None, **kwargs):
        """The operation is used to retrieve search results through the use of the HTTP protocol
        with method type POST.

        :param str query_text: The query text of the search query.
        :param list[str] select_properties: Specifies a property bag of key value pairs.
        :param bool trim_duplicates:  Specifies whether duplicates are removed by the protocol server before sorting,
             selecting, and sending the search results.
        :param int row_limit: The number of search results the protocol client wants to receive, starting at the index
            specified in the StartRow element. The RowLimit value MUST be greater than or equal to zero.
        """
        return_type = ClientResult(self.context, SearchResult())
        request = SearchRequest(query_text=query_text, select_properties=select_properties,
                                trim_duplicates=trim_duplicates, row_limit=row_limit, **kwargs)
        qry = ServiceOperationQuery(self, "postquery", None, request, "request", return_type)
        self.context.add_query(qry)
        return return_type

    def record_page_click(self, page_info=None, click_type=None, block_type=None):
        """This operation is used by the protocol client to inform the protocol server that a user clicked a
        query result on a page. When a click happens, the protocol client sends the details about the click
        and the page impression for which the query result was clicked to the protocol server.
        This operation MUST NOT be used if no query logging information is returned for a query.
        Also this operation MUST NOT be used if a user clicks a query result for which query logging
        information was not returned

        :param str page_info: Specifies the information about the clicked page, the page impression.
        :param str click_type: Type of clicks. If a particular query result is clicked then the click type returned
             by the search service for this query result MUST be used. If "more" link is clicked then "ClickMore"
             click type MUST be used.
        :param str block_type: Type of query results in the page impression block
        """
        payload = {
            "pageInfo": page_info,
            "clickType": click_type,
            "blockType": block_type
        }
        qry = ServiceOperationQuery(self, "RecordPageClick", None, payload)
        self.context.add_query(qry)
        return self

    def search_center_url(self):
        """The operation is used to get the URI address of the search center by using the HTTP protocol
        with the GET method. The operation returns the URI of the of the search center."""
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "searchCenterUrl", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def results_page_address(self):
        """The operation is used to get the URI address of the result page by using the HTTP protocol
        with the GET method. The operation returns the URI of the result page."""
        pass

    def suggest(self, query_text):
        """
        :param str query_text: The query text of the search query. If this element is not present or a value
             is not specified, a default value of an empty string MUST be used, and the server MUST return a
             FaultException<ExceptionDetail> message.
        """
        return_type = ClientResult(self.context, QuerySuggestionResults())
        payload = {
            "querytext": query_text
        }
        qry = ServiceOperationQuery(self, "suggest", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def auto_completions(self, query_text, sources=None, number_of_completions=None, cursor_position=None):
        """
        The operation is used to retrieve auto completion results by using the HTTP protocol with the GET method.

        :param str query_text: The query text of the search query. If this element is not present or a value is not
             specified, a default value of an empty string MUST be used, and the server MUST return
             a FaultException<ExceptionDetail> message.
        :param str sources: Specifies the sources that the protocol server SHOULD use when computing the result.
            If NULL, the protocol server SHOULD use all of the sources for autocompletions. The value SHOULD be a
            comma separated set of sources for autocompletions. The set of available sources the server SHOULD support
            is "Tag", which MAY be compiled from the set of #tags applied to documents. If the sources value is not
            a comma separated set of sources, or any of the source does not match "Tag", the server SHOULD return
            completions from all available sources.
        :param int number_of_completions: Specifies the maximum number query completion results in
            GetQueryCompletionsResponse response message.
        :param int cursor_position: Specifies the cursor position in the query text when this operation is sent
            to the protocol server.
        """
        return_type = ClientResult(self.context, QueryAutoCompletionResults())
        payload = {
            "querytext": query_text,
            "sources": sources,
            "numberOfCompletions": number_of_completions,
            "cursorPosition": cursor_position
        }
        qry = ServiceOperationQuery(self, "autocompletions", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type
