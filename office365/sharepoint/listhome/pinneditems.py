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


class PinnedItems(Entity):
    @staticmethod
    def add_item(context: ClientContext, pinned_item: FavoriteListHomeItem) -> ClientResult[FavoriteListHomeItem]:
        """AddItem operation.

        Args:
            pinned_item (FavoriteListHomeItem):
                pinnedItem parameter
        """
        from office365.sharepoint.listhome.favorite_item import FavoriteListHomeItem
        from office365.sharepoint.listhome.pinneditems import PinnedItems

        return_type = ClientResult(context, FavoriteListHomeItem())
        qry = ServiceOperationQuery(
            PinnedItems(context), "AddItem", None, {"pinnedItem": pinned_item}, None, return_type, True
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_items_by(
        context: ClientContext, site_id: str, list_id: str
    ) -> ClientResult[ClientValueCollection[FavoriteListHomeItem]]:
        """GetItemsBy operation.

        Args:
            site_id (str):
                siteId parameter
            list_id (str):
                listId parameter
        """
        from office365.sharepoint.listhome.favorite_item import FavoriteListHomeItem
        from office365.sharepoint.listhome.pinneditems import PinnedItems

        return_type = ClientResult(context, ClientValueCollection[FavoriteListHomeItem]())
        qry = FunctionQuery(PinnedItems(context), "GetItemsBy", [site_id, list_id], return_type)
        context.add_query(qry)
        return return_type

    @staticmethod
    def remove_item(
        context: ClientContext, site_id: str, list_id: str, web_id: str
    ) -> ClientResult[FavoriteListHomeItem]:
        """RemoveItem operation.

        Args:
            site_id (str):
                siteId parameter
            list_id (str):
                listId parameter
            web_id (str):
                webId parameter
        """
        from office365.sharepoint.listhome.favorite_item import FavoriteListHomeItem
        from office365.sharepoint.listhome.pinneditems import PinnedItems

        return_type = ClientResult(context, FavoriteListHomeItem())
        qry = ServiceOperationQuery(
            PinnedItems(context),
            "RemoveItem",
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
        item_to_reorder: FavoriteListHomeItem,
        item_before: FavoriteListHomeItem,
        item_after: FavoriteListHomeItem,
    ) -> None:
        """ReorderList operation.

        Args:
            item_to_reorder (FavoriteListHomeItem):
                itemToReorder parameter
            item_before (FavoriteListHomeItem):
                itemBefore parameter
            item_after (FavoriteListHomeItem):
                itemAfter parameter
        """
        from office365.sharepoint.listhome.pinneditems import PinnedItems

        qry = ServiceOperationQuery(
            PinnedItems(context),
            "ReorderList",
            None,
            {"itemToReorder": item_to_reorder, "itemBefore": item_before, "itemAfter": item_after},
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def update_item(context: ClientContext, pinned_item: FavoriteListHomeItem) -> ClientResult[FavoriteListHomeItem]:
        """UpdateItem operation.

        Args:
            pinned_item (FavoriteListHomeItem):
                pinnedItem parameter
        """
        from office365.sharepoint.listhome.favorite_item import FavoriteListHomeItem
        from office365.sharepoint.listhome.pinneditems import PinnedItems

        return_type = ClientResult(context, FavoriteListHomeItem())
        qry = ServiceOperationQuery(
            PinnedItems(context), "UpdateItem", None, {"pinnedItem": pinned_item}, None, return_type, True
        )
        context.add_query(qry)
        return return_type
