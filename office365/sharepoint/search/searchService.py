from office365.runtime.client_result import ClientResult
from office365.runtime.resource_path import ResourcePath
from office365.runtime.queries.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.search.query.querySuggestionResults import QuerySuggestionResults
from office365.sharepoint.search.searchResult import SearchResult


class SearchService(BaseEntity):

    def __init__(self, context):
        super().__init__(context, ResourcePath("Microsoft.Office.Server.Search.REST.SearchService"))

    def export(self, user_name, start_time):
        """
        The operation is used by the administrator to retrieve the query log entries,
        issued after a specified date, for a specified user.

        :param datetime.datetime start_time: The timestamp of the oldest query log entry returned.
        :param str user_name: The name of the user that issued the queries."""
        result = ClientResult(None)
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

    def query(self):
        """The operation is used to retrieve search results by using the HTTP protocol with the GET method."""
        pass

    def post_query(self, request):
        """The operation is used to retrieve search results through the use of the HTTP protocol
        with method type POST.

        :type request: SearchRequest"""
        result = SearchResult()
        qry = ServiceOperationQuery(self, "postquery", None, request, "request", result)
        self.context.add_query(qry)
        return result

    def record_page_click(self):
        """The operation is used to record page clicks"""
        pass

    def search_center_url(self):
        """The operation is used to get the URI address of the search center by using the HTTP protocol
        with the GET method. The operation returns the URI of the of the search center."""
        result = ClientResult(None)
        qry = ServiceOperationQuery(self, "searchCenterUrl", None, None, None, result)
        self.context.add_query(qry)
        return result

    def results_page_address(self):
        """The operation is used to get the URI address of the result page by using the HTTP protocol
        with the GET method. The operation returns the URI of the result page."""
        pass

    def suggest(self, query_text):
        result = QuerySuggestionResults()
        payload = {
            "querytext": query_text
        }
        qry = ServiceOperationQuery(self, "suggest", None, payload, None, result)
        self.context.add_query(qry)
        return result
