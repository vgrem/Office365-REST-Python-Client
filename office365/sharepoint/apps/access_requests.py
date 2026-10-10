from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class AccessRequests(Entity):
    """ """

    @staticmethod
    def change_request_status(
        context: ClientContext, item_id: int, new_status: int, conv_str: str, perm_type: str, permission_level: int
    ) -> None:
        """ChangeRequestStatus operation.

        Args:
            item_id (int):
                itemId parameter
            new_status (int):
                newStatus parameter
            conv_str (str):
                convStr parameter
            perm_type (str):
                permType parameter
            permission_level (int):
                permissionLevel parameter
        """
        from office365.sharepoint.apps.access_requests import AccessRequests

        qry = ServiceOperationQuery(
            AccessRequests(context),
            "ChangeRequestStatus",
            None,
            {
                "itemId": item_id,
                "newStatus": new_status,
                "convStr": conv_str,
                "permType": perm_type,
                "permissionLevel": permission_level,
            },
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def change_request_status_bulk(context: ClientContext, request_ids: list[int], new_status: int) -> None:
        """ChangeRequestStatusBulk operation.

        Args:
            request_ids (list[int]):
                requestIds parameter
            new_status (int):
                newStatus parameter
        """
        from office365.sharepoint.apps.access_requests import AccessRequests

        qry = ServiceOperationQuery(
            AccessRequests(context),
            "ChangeRequestStatusBulk",
            None,
            {"requestIds": ClientValueCollection(int, request_ids), "newStatus": new_status},
            None,
            None,
            True,
        )
        context.add_query(qry)
