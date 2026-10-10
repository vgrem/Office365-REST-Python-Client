from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.listhome.favorite_item import FavoriteListHomeItem


class FavoriteLists(Entity):
    @property
    def entity_type_name(self):
        return "SP.FavoriteLists"

    @staticmethod
    def add_list(context: ClientContext, favorite_list: FavoriteListHomeItem) -> ClientResult[FavoriteListHomeItem]:
        """AddList operation.

        Args:
            favorite_list (FavoriteListHomeItem):
                favoriteList parameter
        """
        from office365.sharepoint.listhome.favorite_item import FavoriteListHomeItem
        from office365.sharepoint.listhome.favorite_lists import FavoriteLists

        return_type = ClientResult(context, FavoriteListHomeItem())
        qry = ServiceOperationQuery(
            FavoriteLists(context), "AddList", None, {"favoriteList": favorite_list}, None, return_type, True
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_lists_by(
        context: ClientContext, site_id: str, list_id: str, page: int
    ) -> ClientResult[ClientValueCollection[FavoriteListHomeItem]]:
        """GetListsBy operation.

        Args:
            site_id (str):
                siteId parameter
            list_id (str):
                listId parameter
            page (int):
                page parameter
        """
        from office365.sharepoint.listhome.favorite_item import FavoriteListHomeItem
        from office365.sharepoint.listhome.favorite_lists import FavoriteLists

        return_type = ClientResult(context, ClientValueCollection[FavoriteListHomeItem]())
        qry = FunctionQuery(FavoriteLists(context), "GetListsBy", [site_id, list_id, page], return_type)
        context.add_query(qry)
        return return_type

    @staticmethod
    def remove_list(
        context: ClientContext, site_id: str, list_id: str, web_id: str
    ) -> ClientResult[FavoriteListHomeItem]:
        """RemoveList operation.

        Args:
            site_id (str):
                siteId parameter
            list_id (str):
                listId parameter
            web_id (str):
                webId parameter
        """
        from office365.sharepoint.listhome.favorite_item import FavoriteListHomeItem
        from office365.sharepoint.listhome.favorite_lists import FavoriteLists

        return_type = ClientResult(context, FavoriteListHomeItem())
        qry = ServiceOperationQuery(
            FavoriteLists(context),
            "RemoveList",
            None,
            {"siteId": site_id, "listId": list_id, "webId": web_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def reorder_list(
        context: ClientContext,
        list_to_reorder: FavoriteListHomeItem,
        list_before: FavoriteListHomeItem,
        list_after: FavoriteListHomeItem,
    ) -> None:
        """ReorderList operation.

        Args:
            list_to_reorder (FavoriteListHomeItem):
                listToReorder parameter
            list_before (FavoriteListHomeItem):
                listBefore parameter
            list_after (FavoriteListHomeItem):
                listAfter parameter
        """
        from office365.sharepoint.listhome.favorite_lists import FavoriteLists

        qry = ServiceOperationQuery(
            FavoriteLists(context),
            "ReorderList",
            None,
            {"listToReorder": list_to_reorder, "listBefore": list_before, "listAfter": list_after},
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def update_list(context: ClientContext, favorite_list: FavoriteListHomeItem) -> ClientResult[FavoriteListHomeItem]:
        """UpdateList operation.

        Args:
            favorite_list (FavoriteListHomeItem):
                favoriteList parameter
        """
        from office365.sharepoint.listhome.favorite_item import FavoriteListHomeItem
        from office365.sharepoint.listhome.favorite_lists import FavoriteLists

        return_type = ClientResult(context, FavoriteListHomeItem())
        qry = ServiceOperationQuery(
            FavoriteLists(context), "UpdateList", None, {"favoriteList": favorite_list}, None, return_type, True
        )
        context.add_query(qry)
        return return_type
