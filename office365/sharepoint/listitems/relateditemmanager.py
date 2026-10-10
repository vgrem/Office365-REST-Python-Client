from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.listitems.relateditem import RelatedItem


class RelatedItemManager(Entity):
    @staticmethod
    def add_single_link(
        context: ClientContext,
        source_list_name: str,
        source_item_id: int,
        source_web_url: str,
        target_list_name: str,
        target_item_id: int,
        target_web_url: str,
        try_add_reverse_link: bool,
    ) -> None:
        """AddSingleLink operation.

        Args:
            source_list_name (str):
                SourceListName parameter
            source_item_id (int):
                SourceItemID parameter
            source_web_url (str):
                SourceWebUrl parameter
            target_list_name (str):
                TargetListName parameter
            target_item_id (int):
                TargetItemID parameter
            target_web_url (str):
                TargetWebUrl parameter
            try_add_reverse_link (bool):
                TryAddReverseLink parameter
        """
        from office365.sharepoint.listitems.relateditemmanager import RelatedItemManager

        qry = ServiceOperationQuery(
            RelatedItemManager(context),
            "AddSingleLink",
            None,
            {
                "SourceListName": source_list_name,
                "SourceItemID": source_item_id,
                "SourceWebUrl": source_web_url,
                "TargetListName": target_list_name,
                "TargetItemID": target_item_id,
                "TargetWebUrl": target_web_url,
                "TryAddReverseLink": try_add_reverse_link,
            },
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def add_single_link_from_url(
        context: ClientContext,
        source_item_url: str,
        target_list_name: str,
        target_item_id: int,
        try_add_reverse_link: bool,
    ) -> None:
        """AddSingleLinkFromUrl operation.

        Args:
            source_item_url (str):
                SourceItemUrl parameter
            target_list_name (str):
                TargetListName parameter
            target_item_id (int):
                TargetItemID parameter
            try_add_reverse_link (bool):
                TryAddReverseLink parameter
        """
        from office365.sharepoint.listitems.relateditemmanager import RelatedItemManager

        qry = ServiceOperationQuery(
            RelatedItemManager(context),
            "AddSingleLinkFromUrl",
            None,
            {
                "SourceItemUrl": source_item_url,
                "TargetListName": target_list_name,
                "TargetItemID": target_item_id,
                "TryAddReverseLink": try_add_reverse_link,
            },
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def add_single_link_to_url(
        context: ClientContext,
        source_list_name: str,
        source_item_id: int,
        target_item_url: str,
        try_add_reverse_link: bool,
    ) -> None:
        """AddSingleLinkToUrl operation.

        Args:
            source_list_name (str):
                SourceListName parameter
            source_item_id (int):
                SourceItemID parameter
            target_item_url (str):
                TargetItemUrl parameter
            try_add_reverse_link (bool):
                TryAddReverseLink parameter
        """
        from office365.sharepoint.listitems.relateditemmanager import RelatedItemManager

        qry = ServiceOperationQuery(
            RelatedItemManager(context),
            "AddSingleLinkToUrl",
            None,
            {
                "SourceListName": source_list_name,
                "SourceItemID": source_item_id,
                "TargetItemUrl": target_item_url,
                "TryAddReverseLink": try_add_reverse_link,
            },
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def delete_single_link(
        context: ClientContext,
        source_list_name: str,
        source_item_id: int,
        source_web_url: str,
        target_list_name: str,
        target_item_id: int,
        target_web_url: str,
        try_delete_reverse_link: bool,
    ) -> None:
        """DeleteSingleLink operation.

        Args:
            source_list_name (str):
                SourceListName parameter
            source_item_id (int):
                SourceItemID parameter
            source_web_url (str):
                SourceWebUrl parameter
            target_list_name (str):
                TargetListName parameter
            target_item_id (int):
                TargetItemID parameter
            target_web_url (str):
                TargetWebUrl parameter
            try_delete_reverse_link (bool):
                TryDeleteReverseLink parameter
        """
        from office365.sharepoint.listitems.relateditemmanager import RelatedItemManager

        qry = ServiceOperationQuery(
            RelatedItemManager(context),
            "DeleteSingleLink",
            None,
            {
                "SourceListName": source_list_name,
                "SourceItemID": source_item_id,
                "SourceWebUrl": source_web_url,
                "TargetListName": target_list_name,
                "TargetItemID": target_item_id,
                "TargetWebUrl": target_web_url,
                "TryDeleteReverseLink": try_delete_reverse_link,
            },
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def get_page_one_related_items(
        context: ClientContext, source_list_name: str, source_item_id: int
    ) -> ClientResult[ClientValueCollection[RelatedItem]]:
        """GetPageOneRelatedItems operation.

        Args:
            source_list_name (str):
                SourceListName parameter
            source_item_id (int):
                SourceItemID parameter
        """
        from office365.sharepoint.listitems.relateditem import RelatedItem
        from office365.sharepoint.listitems.relateditemmanager import RelatedItemManager

        return_type = ClientResult(context, ClientValueCollection[RelatedItem]())
        qry = FunctionQuery(
            RelatedItemManager(context), "GetPageOneRelatedItems", [source_list_name, source_item_id], return_type
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_related_items(
        context: ClientContext, source_list_name: str, source_item_id: int
    ) -> ClientResult[ClientValueCollection[RelatedItem]]:
        """GetRelatedItems operation.

        Args:
            source_list_name (str):
                SourceListName parameter
            source_item_id (int):
                SourceItemID parameter
        """
        from office365.sharepoint.listitems.relateditem import RelatedItem
        from office365.sharepoint.listitems.relateditemmanager import RelatedItemManager

        return_type = ClientResult(context, ClientValueCollection[RelatedItem]())
        qry = FunctionQuery(
            RelatedItemManager(context), "GetRelatedItems", [source_list_name, source_item_id], return_type
        )
        context.add_query(qry)
        return return_type
