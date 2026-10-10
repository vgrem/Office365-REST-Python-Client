from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.listhome.favorite_item import FavoriteListHomeItem


class FavoriteListsSubstrate(Entity):
    @staticmethod
    def add_list(
        context: ClientContext, list_: FavoriteListHomeItem, content_source: str, query: str
    ) -> ClientResult[str]:
        """AddList operation.

        Args:
            list_ (FavoriteListHomeItem):
                list parameter
            content_source (str):
                contentSource parameter
            query (str):
                query parameter
        """
        from office365.sharepoint.listhome.favoritelistssubstrate import (
            FavoriteListsSubstrate,
        )

        return_type = ClientResult(context, str())
        qry = ServiceOperationQuery(
            FavoriteListsSubstrate(context),
            "AddList",
            None,
            {"list": list_, "contentSource": content_source, "query": query},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_lists_by(context: ClientContext, site_id: str, list_id: str, page: int) -> ClientResult[str]:
        """GetListsBy operation.

        Args:
            site_id (str):
                siteId parameter
            list_id (str):
                listId parameter
            page (int):
                page parameter
        """
        from office365.sharepoint.listhome.favoritelistssubstrate import (
            FavoriteListsSubstrate,
        )

        return_type = ClientResult(context, str())
        qry = FunctionQuery(FavoriteListsSubstrate(context), "GetListsBy", [site_id, list_id, page], return_type)
        context.add_query(qry)
        return return_type

    @staticmethod
    def remove_list(context: ClientContext, site_id: str, list_id: str, web_id: str) -> None:
        """RemoveList operation.

        Args:
            site_id (str):
                siteId parameter
            list_id (str):
                listId parameter
            web_id (str):
                webId parameter
        """
        from office365.sharepoint.listhome.favoritelistssubstrate import (
            FavoriteListsSubstrate,
        )

        qry = ServiceOperationQuery(
            FavoriteListsSubstrate(context),
            "RemoveList",
            None,
            {"siteId": site_id, "listId": list_id, "webId": web_id},
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def update_list(context: ClientContext, list_: FavoriteListHomeItem) -> None:
        """UpdateList operation.

        Args:
            list_ (FavoriteListHomeItem):
                list parameter
        """
        from office365.sharepoint.listhome.favoritelistssubstrate import (
            FavoriteListsSubstrate,
        )

        qry = ServiceOperationQuery(
            FavoriteListsSubstrate(context), "UpdateList", None, {"list": list_}, None, None, True
        )
        context.add_query(qry)
