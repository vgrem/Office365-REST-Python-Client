from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class SPPlaylist(Entity):
    @staticmethod
    def subscribe(context: ClientContext, list_id: str) -> None:
        """Subscribe operation.

        Args:
            list_id (str):
                listId parameter
        """
        from office365.sharepoint.lists.playlist import SPPlaylist

        qry = ServiceOperationQuery(SPPlaylist(context), "Subscribe", None, {"listId": list_id}, None, None, True)
        context.add_query(qry)

    @staticmethod
    def unsubscribe(context: ClientContext, list_id: str) -> None:
        """Unsubscribe operation.

        Args:
            list_id (str):
                listId parameter
        """
        from office365.sharepoint.lists.playlist import SPPlaylist

        qry = ServiceOperationQuery(SPPlaylist(context), "Unsubscribe", None, {"listId": list_id}, None, None, True)
        context.add_query(qry)
