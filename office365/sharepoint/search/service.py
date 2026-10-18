from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional, Union

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.v3.static import StaticPath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity
from office365.sharepoint.principal.users.user import User
from office365.sharepoint.search.query.auto_completion_results import QueryAutoCompletionResults
from office365.sharepoint.search.query.popular_tenant_query import PopularTenantQuery
from office365.sharepoint.search.query.sort.sort import Sort
from office365.sharepoint.search.query.suggestion_results import QuerySuggestionResults
from office365.sharepoint.search.query.tenant_custom_query_suggestions import TenantCustomQuerySuggestions
from office365.sharepoint.search.request import SearchRequest
from office365.sharepoint.search.result import SearchResult


class SearchService(Entity):
    """SearchService exposes OData Service Operations."""

    @property
    def resource_path(self):
        if self._resource_path is None:
            self._resource_path = StaticPath("Microsoft.Office.Server.Search.REST.SearchService")
        return self._resource_path

    def export(self, user: Union[str, User], start_time: datetime) -> ClientResult[str]:
        """The operation is used by the administrator to retrieve the query log entries,
        issued after a specified date, for a specified user.

        Args:
            start_time (datetime.datetime): The timestamp of the oldest query log entry returned.
            user (str or User): The name of the user or user object that issued the queries.
        """
        return_type = ClientResult(self.context, str())

        def _export(user_name: str | None):
            assert user_name is not None
            payload = {"userName": user_name, "startTime": start_time.isoformat()}
            qry = ServiceOperationQuery(self, "export", None, payload, None, return_type)
            self.context.add_query(qry)

        if isinstance(user, User):
            user.ensure_property("UserPrincipalName").after_execute(
                lambda _: _export(user.user_principal_name) if user.user_principal_name is not None else None
            )
        else:
            _export(user)
        return return_type

    def export_manual_suggestions(self) -> ClientResult[TenantCustomQuerySuggestions]:
        """ """
        return_type = ClientResult(self.context, TenantCustomQuerySuggestions())
        qry = ServiceOperationQuery(self, "exportmanualsuggestions", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def export_popular_tenant_queries(self, count: int) -> ClientResult[ClientValueCollection[PopularTenantQuery]]:
        """This method is used to get a list of popular search queries executed on the tenant.

        Args:
            count (int):
        """
        return_type = ClientResult(self.context, ClientValueCollection(PopularTenantQuery))
        payload = {"count": count}
        qry = ServiceOperationQuery(self, "exportpopulartenantqueries", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def query(
        self,
        query_text: str,
        source_id: Optional[str] = None,
        ranking_model_id=None,
        start_row=None,
        row_limit=None,
        rows_per_page=None,
        select_properties=None,
        refinement_filters=None,
        refiners=None,
        sort_list=None,
        trim_duplicates=None,
        enable_query_rules=None,
        enable_sorting=None,
        **kwargs,
    ):
        """The operation is used to retrieve search results by using the HTTP protocol with the GET method.

        Args:
            query_text (str): The query text of the search query.
            source_id (str): Specifies the unique identifier for result source to use for executing the search query.
              If no value is specified then the protocol server MUST use the id for the default result source.
            ranking_model_id (str): The GUID of the ranking model that SHOULD be used for this search query.
              If this element is not present or a value is not specified, the protocol server MUST use the default
              ranking model, according to protocol server configuration.
            start_row (int): A zero-based index of the first search result in the list of all search results the
              protocol server returns. The StartRow value MUST be greater than or equal to zero.
            rows_per_page (int): The number of result items the protocol client displays per page. If this element
              is set to an integer value less than 1, the value of the RowLimit element MUST be used as the
              default value.
            row_limit (int): The number of search results the protocol client wants to receive, starting at
              the index specified in the StartRow element. The RowLimit value MUST be greater than or equal to zero.
            select_properties (list[str]): Specifies a property bag of key value pairs.
            refinement_filters (list[str]): The list of refinement tokens for drilldown into search results
            refiners (list[str]): Specifies a list of refiners
            sort_list (list[Sort]): Specifies the list of properties with which to sort the search results.
            trim_duplicates (bool): Specifies whether duplicates are removed by the protocol server before sorting,
              selecting, and sending the search results.
            enable_sorting (bool): Specifies whether sorting of results is enabled or not. MUST ignore the SortList
              specified if this value is set to false.
            enable_query_rules (bool): Specifies whether query rules are included when a search query is executed.
              If the value is true, query rules are applied in the search query. If the value is false, query rules
              MUST NOT be applied in the search query.
        """
        params = {
            "querytext": query_text,
            "sourceId": source_id,
            "rankingModelId": ranking_model_id,
            "startRow": start_row,
            "rowsPerPage": rows_per_page,
            "trimDuplicates": trim_duplicates,
            "rowLimit": row_limit,
            "enableQueryRules": enable_query_rules,
            "enableSorting": enable_sorting,
        }
        if refinement_filters:
            params["refinementFilters"] = ",".join(refinement_filters)
        if sort_list:
            params["sortList"] = ",".join((str(s) for s in sort_list))
        if select_properties:
            params["selectProperties"] = ",".join(select_properties)
        if refiners:
            params["refiners"] = ",".join(refiners)
        params.update(**kwargs)
        return_type: ClientResult[SearchResult] = ClientResult(self.context, SearchResult())
        qry = FunctionQuery(self, "query", params, return_type)
        self.context.add_query(qry)
        return return_type

    def post_query(
        self,
        query_text: str,
        select_properties: Optional[List[str]] = None,
        trim_duplicates: Optional[bool] = None,
        row_limit: Optional[int] = None,
        enable_sorting: Optional[bool] = None,
        sort_list: Optional[List[Sort]] = None,
        **kwargs: Any,
    ) -> ClientResult[SearchResult]:
        """The operation is used to retrieve search results through the use of the HTTP protocol
        with method type POST.

        Args:
            query_text (str): The query text of the search query.
            select_properties (list[str]): Specifies a property bag of key value pairs.
            trim_duplicates (bool): Specifies whether duplicates are removed by the protocol server before sorting,
              selecting, and sending the search results.
            row_limit (int): The number of search results the protocol client wants to receive, starting at the index
              specified in the StartRow element. The RowLimit value MUST be greater than or equal to zero.
            enable_sorting (bool): Specifies whether sorting of results is enabled or not. MUST ignore the SortList
              specified if this value is set to false.
            sort_list (list[Sort]): Specifies the list of properties with which to sort the search results, so the
              request body carries the same sorting the GET form spells as ``sortList``.
        """
        return_type = ClientResult(self.context, SearchResult())
        request = SearchRequest(
            Querytext=query_text,
            SelectProperties=StringCollection(select_properties) if select_properties else StringCollection(),
            TrimDuplicates=trim_duplicates if trim_duplicates is not None else False,
            RowLimit=row_limit,
            EnableSorting=enable_sorting,
            SortList=ClientValueCollection(Sort, sort_list) if sort_list else ClientValueCollection(Sort),
            **kwargs,
        )
        payload = {"request": request}
        qry = ServiceOperationQuery(self, "postquery", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def record_page_click(self, page_info=None, click_type=None, block_type=None):
        """This operation is used by the protocol client to inform the protocol server that a user clicked a
        query result on a page. When a click happens, the protocol client sends the details about the click
        and the page impression for which the query result was clicked to the protocol server.
        This operation MUST NOT be used if no query logging information is returned for a query.
        Also this operation MUST NOT be used if a user clicks a query result for which query logging
        information was not returned

        Args:
            page_info (str): Specifies the information about the clicked page, the page impression.
            click_type (str): Type of clicks. If a particular query result is clicked then the click type returned by
              the search service for this query result MUST be used. If "more" link is clicked then "ClickMore" click
              type MUST be used.
            block_type (str): Type of query results in the page impression block
        """
        payload = {"pageInfo": page_info, "clickType": click_type, "blockType": block_type}
        qry = ServiceOperationQuery(self, "RecordPageClick", None, payload)
        self.context.add_query(qry)
        return self

    def search_center_url(self) -> ClientResult[str]:
        """The operation is used to get the URI address of the search center by using the HTTP protocol
        with the GET method. The operation returns the URI of the of the search center.
        """
        return_type = ClientResult[str](self.context)
        qry = ServiceOperationQuery(self, "searchCenterUrl", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def results_page_address(self) -> ClientResult[str]:
        """The operation is used to get the URI address of the result page by using the HTTP protocol
        with the GET method. The operation returns the URI of the result page."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "resultspageaddress", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def suggest(self, query_text: str) -> ClientResult[QuerySuggestionResults]:
        """Args:
        query_text (str): The query text of the search query. If this element is not present or a value is
          not specified, a default value of an empty string MUST be used, and the server MUST return
          a FaultException<ExceptionDetail> message.
        """
        return_type = ClientResult(self.context, QuerySuggestionResults())
        payload = {"querytext": query_text}
        qry = ServiceOperationQuery(self, "suggest", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def auto_completions(
        self,
        query_text: str,
        sources: Optional[str] = None,
        number_of_completions: Optional[int] = None,
        cursor_position: Optional[int] = None,
    ) -> ClientResult[QueryAutoCompletionResults]:
        """The operation is used to retrieve auto completion results by using the HTTP protocol with the GET method.

        Args:
            query_text (str): The query text of the search query. If this element is not present or a value
              is not specified, a default value of an empty string MUST be used, and the server MUST return a
              FaultException<ExceptionDetail> message.
            sources (str): Specifies the sources that the protocol server SHOULD use when computing the result.
               If NULL, the protocol server SHOULD use all of the sources for autocompletions.
               The value SHOULD be a comma separated set of sources for autocompletions. The set of available
               sources the server SHOULD support is "Tag", which MAY be compiled from the set of #tags applied
               to documents. If the sources value is not a comma separated set of sources, or any of the source
               does not match "Tag", the server SHOULD return completions from all available sources.
            number_of_completions (int): Specifies the maximum number query completion results in
               etQueryCompletionsResponse response message.
            cursor_position (int): Specifies the cursor position in the query text when this operation
               is sent to the protocol server.
        """
        return_type = ClientResult(self.context, QueryAutoCompletionResults())
        payload = {
            "querytext": query_text,
            "sources": sources,
            "numberOfCompletions": number_of_completions,
            "cursorPosition": cursor_position,
        }
        qry = ServiceOperationQuery(self, "autocompletions", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Office.Server.Search.REST.SearchService"

    def autocompletions(
        self, querytext: str, sources: str, number_of_completions: int, cursor_position: int
    ) -> ClientResult[QueryAutoCompletionResults]:
        """autocompletions operation.

        Args:
            querytext (str): querytext parameter
            sources (str): sources parameter
            number_of_completions (int): numberOfCompletions parameter
            cursor_position (int): cursorPosition parameter
        """
        return_type = ClientResult(self.context, QueryAutoCompletionResults())
        qry = FunctionQuery(
            self, "autocompletions", [querytext, sources, number_of_completions, cursor_position], return_type
        )
        self.context.add_query(qry)
        return return_type

    def exportmanualsuggestions(self) -> ClientResult[TenantCustomQuerySuggestions]:
        """exportmanualsuggestions operation."""
        return_type = ClientResult(self.context, TenantCustomQuerySuggestions())
        qry = FunctionQuery(self, "exportmanualsuggestions", [], return_type)
        self.context.add_query(qry)
        return return_type

    def exportpopulartenantqueries(self, count: int) -> ClientResult[ClientValueCollection[PopularTenantQuery]]:
        """exportpopulartenantqueries operation.

        Args:
            count (int): count parameter
        """
        return_type = ClientResult(self.context, ClientValueCollection[PopularTenantQuery]())
        qry = FunctionQuery(self, "exportpopulartenantqueries", [count], return_type)
        self.context.add_query(qry)
        return return_type

    def postquery(self, request: SearchRequest) -> ClientResult[SearchResult]:
        """postquery operation.

        Args:
            request (SearchRequest): request parameter
        """
        return_type = ClientResult(self.context, SearchResult())
        qry = FunctionQuery(self, "postquery", [request], return_type)
        self.context.add_query(qry)
        return return_type

    def resultspageaddress(self) -> ClientResult[str]:
        """resultspageaddress operation."""
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "resultspageaddress", [], return_type)
        self.context.add_query(qry)
        return return_type

    def searchcenterurl(self) -> ClientResult[str]:
        """searchcenterurl operation."""
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "searchcenterurl", [], return_type)
        self.context.add_query(qry)
        return return_type
