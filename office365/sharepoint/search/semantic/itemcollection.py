from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class SemanticSearchItemCollection(Entity):
    @staticmethod
    def get_search_results(context: ClientContext, payload: str, option: str) -> ClientResult[bytes]:
        """GetSearchResults operation.

        Args:
            payload (str):
                payload parameter
            option (str):
                option parameter
        """
        from office365.sharepoint.search.semantic.itemcollection import (
            SemanticSearchItemCollection,
        )

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            SemanticSearchItemCollection(context),
            "GetSearchResults",
            None,
            {"payload": payload, "option": option},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type
