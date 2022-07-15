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
        """"""
        pass

    def export_popular_tenant_queries(self, count):
        """This method is used to get a list of popular search queries executed on the tenant.
        """
        result = ClientResult(self.context, ClientValueCollection(PopularTenantQuery))
        payload = {
            "count": count,
        }
        qry = ServiceOperationQuery(self, "exportpopulartenantqueries", None, payload, None, result)
        self.context.add_query(qry)
        return result

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

    def post_query(self, request):
        """The operation is used to retrieve search results through the use of the HTTP protocol
        with method type POST.

        :type request: office365.sharepoint.search.request.SearchRequest"""
        result = ClientResult(self.context, SearchResult())
        qry = ServiceOperationQuery(self, "postquery", None, request, "request", result)
        self.context.add_query(qry)
        return result

    def record_page_click(self):
        """The operation is used to record page clicks"""
        pass

    def search_center_url(self):
        """The operation is used to get the URI address of the search center by using the HTTP protocol
        with the GET method. The operation returns the URI of the of the search center."""
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "searchCenterUrl", None, None, None, result)
        self.context.add_query(qry)
        return result

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
        result = ClientResult(self.context, QuerySuggestionResults())
        payload = {
            "querytext": query_text
        }
        qry = ServiceOperationQuery(self, "suggest", None, payload, None, result)
        self.context.add_query(qry)
        return result

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
            #"sources": sources,
            #"numberOfCompletions": number_of_completions,
            #"cursorPosition": cursor_position
        }
        qry = ServiceOperationQuery(self, "autocompletions", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type
