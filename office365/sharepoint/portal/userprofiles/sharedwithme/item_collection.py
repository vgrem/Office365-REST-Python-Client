from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class SharedWithMeItemCollection(Entity):
    """"""

    @staticmethod
    def get_shared_with_me_external_items(context, top: int) -> ClientResult[str]:
        """Args:
        context (office365.sharepoint.client_context.ClientContext): Client context
        top (int):
        """
        binding_type = SharedWithMeItemCollection(context)
        return_type = ClientResult(context, str())
        params = {"top": top}
        qry = ServiceOperationQuery(
            binding_type,
            "GetSharedWithMeExternalItems",
            params,
            return_type=return_type,
            is_static=True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_shared_with_me_items(context, top, skip_token=None, include_sharing_history=None):
        """Args:
        context (office365.sharepoint.client_context.ClientContext): Client context
        top (int):
        skip_token (str):
        include_sharing_history (bool):
        """
        binding_type = SharedWithMeItemCollection(context)
        return_type = ClientResult(context, str())
        params = {
            "top": top,
            "skiptoken": skip_token,
            "includeSharingHistory": include_sharing_history,
        }
        qry = ServiceOperationQuery(
            binding_type,
            "GetSharedWithMeItems",
            None,
            params,
            return_type=return_type,
            is_static=True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_calendar_events(context: ClientContext) -> ClientResult[str]:
        """GetCalendarEvents operation."""
        from office365.sharepoint.portal.userprofiles.sharedwithme.item_collection import (
            SharedWithMeItemCollection,
        )

        return_type = ClientResult(context, str())
        qry = FunctionQuery(SharedWithMeItemCollection(context), "GetCalendarEvents", [], return_type)
        context.add_query(qry)
        return return_type

    @staticmethod
    def remove_from_shared_with_me(
        context: ClientContext, spo_ids: str, item_ids: list[str], working_set_ids: list[str]
    ) -> ClientResult[str]:
        """RemoveFromSharedWithMe operation.

        Args:
            spo_ids (str):
                spoIds parameter
            item_ids (list[str]):
                itemIds parameter
            working_set_ids (list[str]):
                workingSetIds parameter
        """
        from office365.sharepoint.portal.userprofiles.sharedwithme.item_collection import (
            SharedWithMeItemCollection,
        )

        return_type = ClientResult(context, str())
        qry = ServiceOperationQuery(
            SharedWithMeItemCollection(context),
            "RemoveFromSharedWithMe",
            None,
            {
                "spoIds": spo_ids,
                "itemIds": StringCollection(item_ids),
                "workingSetIds": StringCollection(working_set_ids),
            },
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def remove_items_from_shared_with_me_view_by_path(
        context: ClientContext, item_paths: ClientValueCollection[ResourcePath]
    ) -> ClientResult[StringCollection]:
        """RemoveItemsFromSharedWithMeViewByPath operation.

        Args:
            item_paths (ClientValueCollection[ResourcePath]):
                itemPaths parameter
        """
        from office365.sharepoint.portal.userprofiles.sharedwithme.item_collection import (
            SharedWithMeItemCollection,
        )

        return_type = ClientResult(context, StringCollection())
        qry = ServiceOperationQuery(
            SharedWithMeItemCollection(context),
            "RemoveItemsFromSharedWithMeViewByPath",
            None,
            {"itemPaths": item_paths},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def restore_items_from_shared_with_me_view_by_path(
        context: ClientContext, item_paths: ClientValueCollection[ResourcePath]
    ) -> ClientResult[StringCollection]:
        """RestoreItemsFromSharedWithMeViewByPath operation.

        Args:
            item_paths (ClientValueCollection[ResourcePath]):
                itemPaths parameter
        """
        from office365.sharepoint.portal.userprofiles.sharedwithme.item_collection import (
            SharedWithMeItemCollection,
        )

        return_type = ClientResult(context, StringCollection())
        qry = ServiceOperationQuery(
            SharedWithMeItemCollection(context),
            "RestoreItemsFromSharedWithMeViewByPath",
            None,
            {"itemPaths": item_paths},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def restore_to_shared_with_me(
        context: ClientContext, spo_ids: str, item_ids: list[str], working_set_ids: list[str]
    ) -> ClientResult[str]:
        """RestoreToSharedWithMe operation.

        Args:
            spo_ids (str):
                spoIds parameter
            item_ids (list[str]):
                itemIds parameter
            working_set_ids (list[str]):
                workingSetIds parameter
        """
        from office365.sharepoint.portal.userprofiles.sharedwithme.item_collection import (
            SharedWithMeItemCollection,
        )

        return_type = ClientResult(context, str())
        qry = ServiceOperationQuery(
            SharedWithMeItemCollection(context),
            "RestoreToSharedWithMe",
            None,
            {
                "spoIds": spo_ids,
                "itemIds": StringCollection(item_ids),
                "workingSetIds": StringCollection(working_set_ids),
            },
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type
