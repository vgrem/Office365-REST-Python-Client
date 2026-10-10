from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class RecentListCollection(Entity):
    @staticmethod
    def get_recent_lists_with_page_context_info(
        context: ClientContext, sort_by: int, template_type_id: str
    ) -> ClientResult[bytes]:
        """GetRecentListsWithPageContextInfo operation.

        Args:
            sort_by (int):
                sortBy parameter
            template_type_id (str):
                templateTypeId parameter
        """
        from office365.sharepoint.lists.recentlistcollection import RecentListCollection

        return_type = ClientResult(context, bytes())
        qry = FunctionQuery(
            RecentListCollection(context),
            "GetRecentListsWithPageContextInfo",
            [sort_by, template_type_id],
            return_type,
            return_raw_content=True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def update_recent_lists(context: ClientContext, recent_lists_json: str) -> None:
        """UpdateRecentLists operation.

        Args:
            recent_lists_json (str):
                recentListsJson parameter
        """
        from office365.sharepoint.lists.recentlistcollection import RecentListCollection

        qry = ServiceOperationQuery(
            RecentListCollection(context),
            "UpdateRecentLists",
            None,
            {"recentListsJson": recent_lists_json},
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def update_recent_lists_remote(context: ClientContext, recent_lists_json: str) -> None:
        """UpdateRecentListsRemote operation.

        Args:
            recent_lists_json (str):
                recentListsJson parameter
        """
        from office365.sharepoint.lists.recentlistcollection import RecentListCollection

        qry = ServiceOperationQuery(
            RecentListCollection(context),
            "UpdateRecentListsRemote",
            None,
            {"recentListsJson": recent_lists_json},
            None,
            None,
            True,
        )
        context.add_query(qry)
