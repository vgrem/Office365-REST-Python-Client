from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class ListHomeItemCollection(Entity):
    @staticmethod
    def get_list_home_items(context: ClientContext, sort_by: int) -> ClientResult[bytes]:
        """GetListHomeItems operation.

        Args:
            sort_by (int):
                sortBy parameter
        """
        from office365.sharepoint.listhome.itemcollection import ListHomeItemCollection

        return_type = ClientResult(context, bytes())
        qry = FunctionQuery(
            ListHomeItemCollection(context), "GetListHomeItems", [sort_by], return_type, return_raw_content=True
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_list_home_items_with_page_context_info(context: ClientContext, sort_by: int) -> ClientResult[bytes]:
        """GetListHomeItemsWithPageContextInfo operation.

        Args:
            sort_by (int):
                sortBy parameter
        """
        from office365.sharepoint.listhome.itemcollection import ListHomeItemCollection

        return_type = ClientResult(context, bytes())
        qry = FunctionQuery(
            ListHomeItemCollection(context),
            "GetListHomeItemsWithPageContextInfo",
            [sort_by],
            return_type,
            return_raw_content=True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_recommend_lists(context: ClientContext) -> ClientResult[str]:
        """GetRecommendLists operation."""
        from office365.sharepoint.listhome.itemcollection import ListHomeItemCollection

        return_type = ClientResult(context, str())
        qry = FunctionQuery(ListHomeItemCollection(context), "GetRecommendLists", [], return_type)
        context.add_query(qry)
        return return_type

    @staticmethod
    def remove_recent_lists(context: ClientContext, recent_lists_json: str) -> None:
        """RemoveRecentLists operation.

        Args:
            recent_lists_json (str):
                recentListsJson parameter
        """
        from office365.sharepoint.listhome.itemcollection import ListHomeItemCollection

        qry = ServiceOperationQuery(
            ListHomeItemCollection(context),
            "RemoveRecentLists",
            None,
            {"recentListsJson": recent_lists_json},
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def remove_recommend_lists(context: ClientContext, recommend_lists_json: str) -> None:
        """RemoveRecommendLists operation.

        Args:
            recommend_lists_json (str):
                recommendListsJson parameter
        """
        from office365.sharepoint.listhome.itemcollection import ListHomeItemCollection

        qry = ServiceOperationQuery(
            ListHomeItemCollection(context),
            "RemoveRecommendLists",
            None,
            {"recommendListsJson": recommend_lists_json},
            None,
            None,
            True,
        )
        context.add_query(qry)
