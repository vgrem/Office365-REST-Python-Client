from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class RecentListProxy(Entity):
    @staticmethod
    def get_recent_lists_proxy(context: ClientContext, sort_by: int, template_type_id: str) -> ClientResult[bytes]:
        """GetRecentListsProxy operation.

        Args:
            sort_by (int):
                sortBy parameter
            template_type_id (str):
                templateTypeId parameter
        """
        from office365.sharepoint.lists.recentlistproxy import RecentListProxy

        return_type = ClientResult(context, bytes())
        qry = FunctionQuery(
            RecentListProxy(context),
            "GetRecentListsProxy",
            [sort_by, template_type_id],
            return_type,
            return_raw_content=True,
        )
        context.add_query(qry)
        return return_type
