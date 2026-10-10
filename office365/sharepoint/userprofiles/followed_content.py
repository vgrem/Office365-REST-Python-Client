from __future__ import annotations

from typing import Optional
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.userprofiles.follow_result import FollowResult
from office365.sharepoint.userprofiles.followed_item import FollowedItem


class FollowedContent(Entity):
    """The FollowedContent class provides access to followed content items."""

    def follow_item(self, item: FollowedItem) -> ClientResult[FollowResult]:
        """The FollowItem method is reserved for server-to-server use only.
        The server sets the specified item to be followed by the current user. This method cannot be called
        from the client.

        Args:
            item (office365.sharepoint.userprofiles.followed_item.FollowedItem): Identifies the item to follow.
        """
        return_type = ClientResult(self.context, FollowResult())
        payload = {"item": item}
        qry = ServiceOperationQuery(self, "FollowItem", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_followed_status(self, url: str) -> ClientResult[int]:
        """The GetFollowedStatus method retrieves the followed status of the specified document or site.
        An item can be followed if the url parameter identifies a document or site that the current user has access to.

        Args:
            url (str): URL that identifies the item
        """
        return_type = ClientResult(self.context, int())
        payload = {"url": url}
        qry = ServiceOperationQuery(self, "GetFollowedStatus", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def followed_documents_url(self) -> Optional[str]:
        """The FollowedDocumentsUrl property gets the location of the followed documents view."""
        return self.properties.get("FollowedDocumentsUrl", None)

    @property
    def followed_sites_url(self) -> Optional[str]:
        """The FollowedSitesUrl property gets the location of the followed sites view."""
        return self.properties.get("FollowedSitesUrl", None)

    @property
    def entity_type_name(self):
        return "SP.UserProfiles.FollowedContent"

    def find_and_update_followed_group(self, group_id: UUID) -> ClientResult[FollowedItem]:
        """FindAndUpdateFollowedGroup operation.

        Args:
            group_id (UUID):
                groupId parameter
        """
        from office365.sharepoint.userprofiles.followed_item import FollowedItem

        return_type = ClientResult(self.context, FollowedItem())
        qry = ServiceOperationQuery(self, "FindAndUpdateFollowedGroup", None, {"groupId": group_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def find_and_update_followed_item(self, url: str) -> ClientResult[FollowedItem]:
        """FindAndUpdateFollowedItem operation.

        Args:
            url (str):
                url parameter
        """
        from office365.sharepoint.userprofiles.followed_item import FollowedItem

        return_type = ClientResult(self.context, FollowedItem())
        qry = ServiceOperationQuery(self, "FindAndUpdateFollowedItem", None, {"url": url}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_groups(self, row_limit: int) -> ClientResult[ClientValueCollection[FollowedItem]]:
        """GetGroups operation.

        Args:
            row_limit (int):
                rowLimit parameter
        """
        from office365.sharepoint.userprofiles.followed_item import FollowedItem

        return_type = ClientResult(self.context, ClientValueCollection[FollowedItem]())
        qry = ServiceOperationQuery(self, "GetGroups", None, {"rowLimit": row_limit}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_item(self, url: str) -> ClientResult[FollowedItem]:
        """GetItem operation.

        Args:
            url (str):
                url parameter
        """
        from office365.sharepoint.userprofiles.followed_item import FollowedItem

        return_type = ClientResult(self.context, FollowedItem())
        qry = ServiceOperationQuery(self, "GetItem", None, {"url": url}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_items(self, options: int, subtype: int) -> ClientResult[ClientValueCollection[FollowedItem]]:
        """GetItems operation.

        Args:
            options (int):
                options parameter
            subtype (int):
                subtype parameter
        """
        from office365.sharepoint.userprofiles.followed_item import FollowedItem

        return_type = ClientResult(self.context, ClientValueCollection[FollowedItem]())
        qry = ServiceOperationQuery(self, "GetItems", None, {"options": options, "subtype": subtype}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def has_group_membership_changed_and_sync_changes(self) -> ClientResult[bool]:
        """HasGroupMembershipChangedAndSyncChanges operation."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "HasGroupMembershipChangedAndSyncChanges", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def is_followed(self, url: str) -> ClientResult[bool]:
        """IsFollowed operation.

        Args:
            url (str):
                url parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "IsFollowed", None, {"url": url}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def refresh_followed_item(self, item: FollowedItem) -> ClientResult[FollowedItem]:
        """RefreshFollowedItem operation.

        Args:
            item (FollowedItem):
                item parameter
        """
        from office365.sharepoint.userprofiles.followed_item import FollowedItem

        return_type = ClientResult(self.context, FollowedItem())
        qry = ServiceOperationQuery(self, "RefreshFollowedItem", None, {"item": item}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def set_item_pin_state(self, uri: str, group_id: UUID, pin_state: int) -> ClientResult[FollowResult]:
        """SetItemPinState operation.

        Args:
            uri (str):
                uri parameter
            group_id (UUID):
                groupId parameter
            pin_state (int):
                pinState parameter
        """
        from office365.sharepoint.userprofiles.follow_result import FollowResult

        return_type = ClientResult(self.context, FollowResult())
        qry = ServiceOperationQuery(
            self, "SetItemPinState", None, {"uri": uri, "groupId": group_id, "pinState": pin_state}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def stop_following(self, url: str) -> Self:
        """StopFollowing operation.

        Args:
            url (str):
                url parameter
        """
        qry = ServiceOperationQuery(self, "StopFollowing", None, {"url": url}, None, None)
        self.context.add_query(qry)
        return self

    def update_followed_group_for_user(self, context_uri: str, group_id: UUID, login_name: str) -> Self:
        """UpdateFollowedGroupForUser operation.

        Args:
            context_uri (str):
                contextUri parameter
            group_id (UUID):
                groupId parameter
            login_name (str):
                loginName parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UpdateFollowedGroupForUser",
            None,
            {"contextUri": context_uri, "groupId": group_id, "loginName": login_name},
            None,
            None,
        )
        self.context.add_query(qry)
        return self
