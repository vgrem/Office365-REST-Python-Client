from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.approvals.createrequestparameters import (
        ApprovalsCreateRequestParameters,
    )
    from office365.sharepoint.approvals.properties import ApprovalsProperties
    from office365.sharepoint.client_context import ClientContext


class Approvals(Entity):
    @staticmethod
    def approve_item_request(
        context: ClientContext, list_id: str, item_id: str, url: str, version: str, approval_id: str, comments: str
    ) -> None:
        """ApproveItemRequest operation.

        Args:
            list_id (str):
                listId parameter
            item_id (str):
                itemId parameter
            url (str):
                url parameter
            version (str):
                version parameter
            approval_id (str):
                approvalId parameter
            comments (str):
                comments parameter
        """
        from office365.sharepoint.approvals.approvals import Approvals

        qry = ServiceOperationQuery(
            Approvals(context),
            "ApproveItemRequest",
            None,
            {
                "listId": list_id,
                "itemId": item_id,
                "url": url,
                "version": version,
                "approvalId": approval_id,
                "comments": comments,
            },
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def cancel_item_request(
        context: ClientContext, list_id: str, item_id: str, url: str, version: str, approval_id: str
    ) -> None:
        """CancelItemRequest operation.

        Args:
            list_id (str):
                listId parameter
            item_id (str):
                itemId parameter
            url (str):
                url parameter
            version (str):
                version parameter
            approval_id (str):
                approvalId parameter
        """
        from office365.sharepoint.approvals.approvals import Approvals

        qry = ServiceOperationQuery(
            Approvals(context),
            "CancelItemRequest",
            None,
            {"listId": list_id, "itemId": item_id, "url": url, "version": version, "approvalId": approval_id},
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def create_item_request(
        context: ClientContext, creation_info: ApprovalsCreateRequestParameters
    ) -> ClientResult[str]:
        """CreateItemRequest operation.

        Args:
            creation_info (ApprovalsCreateRequestParameters):
                creationInfo parameter
        """
        from office365.sharepoint.approvals.approvals import Approvals

        return_type = ClientResult(context, str())
        qry = ServiceOperationQuery(
            Approvals(context), "CreateItemRequest", None, {"creationInfo": creation_info}, None, return_type, True
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def disable(context: ClientContext, list_id: str, view_id: str, reset_all: bool) -> None:
        """Disable operation.

        Args:
            list_id (str):
                listId parameter
            view_id (str):
                viewId parameter
            reset_all (bool):
                resetAll parameter
        """
        from office365.sharepoint.approvals.approvals import Approvals

        qry = ServiceOperationQuery(
            Approvals(context),
            "Disable",
            None,
            {"listId": list_id, "viewId": view_id, "resetAll": reset_all},
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def disable_notifications(context: ClientContext, list_id: str) -> None:
        """DisableNotifications operation.

        Args:
            list_id (str):
                listId parameter
        """
        from office365.sharepoint.approvals.approvals import Approvals

        qry = ServiceOperationQuery(
            Approvals(context), "DisableNotifications", None, {"listId": list_id}, None, None, True
        )
        context.add_query(qry)

    @staticmethod
    def enable(
        context: ClientContext, list_id: str, add_fields_to_default_view: bool, extra_view_to_enable: str
    ) -> None:
        """Enable operation.

        Args:
            list_id (str):
                listId parameter
            add_fields_to_default_view (bool):
                addFieldsToDefaultView parameter
            extra_view_to_enable (str):
                extraViewToEnable parameter
        """
        from office365.sharepoint.approvals.approvals import Approvals

        qry = ServiceOperationQuery(
            Approvals(context),
            "Enable",
            None,
            {
                "listId": list_id,
                "addFieldsToDefaultView": add_fields_to_default_view,
                "extraViewToEnable": extra_view_to_enable,
            },
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def enable_notifications(context: ClientContext, list_id: str) -> None:
        """EnableNotifications operation.

        Args:
            list_id (str):
                listId parameter
        """
        from office365.sharepoint.approvals.approvals import Approvals

        qry = ServiceOperationQuery(
            Approvals(context), "EnableNotifications", None, {"listId": list_id}, None, None, True
        )
        context.add_query(qry)

    @staticmethod
    def get_properties(context: ClientContext, list_id: str) -> ClientResult[ApprovalsProperties]:
        """GetProperties operation.

        Args:
            list_id (str):
                listId parameter
        """
        from office365.sharepoint.approvals.approvals import Approvals
        from office365.sharepoint.approvals.properties import ApprovalsProperties

        return_type = ClientResult(context, ApprovalsProperties())
        qry = FunctionQuery(Approvals(context), "GetProperties", [list_id], return_type)
        context.add_query(qry)
        return return_type

    @staticmethod
    def reject_item_request(
        context: ClientContext, list_id: str, item_id: str, url: str, version: str, approval_id: str, comments: str
    ) -> None:
        """RejectItemRequest operation.

        Args:
            list_id (str):
                listId parameter
            item_id (str):
                itemId parameter
            url (str):
                url parameter
            version (str):
                version parameter
            approval_id (str):
                approvalId parameter
            comments (str):
                comments parameter
        """
        from office365.sharepoint.approvals.approvals import Approvals

        qry = ServiceOperationQuery(
            Approvals(context),
            "RejectItemRequest",
            None,
            {
                "listId": list_id,
                "itemId": item_id,
                "url": url,
                "version": version,
                "approvalId": approval_id,
                "comments": comments,
            },
            None,
            None,
            True,
        )
        context.add_query(qry)

    @staticmethod
    def set_properties(context: ClientContext, list_id: str, properties: ApprovalsProperties) -> None:
        """SetProperties operation.

        Args:
            list_id (str):
                listId parameter
            properties (ApprovalsProperties):
                properties parameter
        """
        from office365.sharepoint.approvals.approvals import Approvals

        qry = ServiceOperationQuery(
            Approvals(context), "SetProperties", None, {"listId": list_id, "properties": properties}, None, None, True
        )
        context.add_query(qry)
