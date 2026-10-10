from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class SearchResultItemCollection(Entity):
    @staticmethod
    def events(context: ClientContext, event_details: str) -> ClientResult[str]:
        """Events operation.

        Args:
            event_details (str):
                eventDetails parameter
        """
        from office365.sharepoint.search.searchresultitemcollection import (
            SearchResultItemCollection,
        )

        return_type = ClientResult(context, str())
        qry = ServiceOperationQuery(
            SearchResultItemCollection(context), "Events", None, {"eventDetails": event_details}, None, return_type, True
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_search_results_as_stream(
        context: ClientContext, text_decorations: int, scenario: str, entitytypes: str, payload: str
    ) -> ClientResult[bytes]:
        """GetSearchResultsAsStream operation.

        Args:
            text_decorations (int):
                textDecorations parameter
            scenario (str):
                scenario parameter
            entitytypes (str):
                entitytypes parameter
            payload (str):
                payload parameter
        """
        from office365.sharepoint.search.searchresultitemcollection import (
            SearchResultItemCollection,
        )

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            SearchResultItemCollection(context),
            "GetSearchResultsAsStream",
            None,
            {"textDecorations": text_decorations, "scenario": scenario, "entitytypes": entitytypes, "payload": payload},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_search_suggestions_as_stream(context: ClientContext, query: str, entitytypes: str) -> ClientResult[bytes]:
        """GetSearchSuggestionsAsStream operation.

        Args:
            query (str):
                query parameter
            entitytypes (str):
                entitytypes parameter
        """
        from office365.sharepoint.search.searchresultitemcollection import (
            SearchResultItemCollection,
        )

        return_type = ClientResult(context, bytes())
        qry = FunctionQuery(
            SearchResultItemCollection(context),
            "GetSearchSuggestionsAsStream",
            [query, entitytypes],
            return_type,
            return_raw_content=True,
        )
        context.add_query(qry)
        return return_type
