from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from typing_extensions import Self

from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.types.property_values import PropertyValues

if TYPE_CHECKING:
    from office365.sharepoint.listitems.listitem import ListItem


class Alert(Entity):
    """
    Represents an alert, which generates periodic e-mail notifications sent to a user about the list, list item,
    document, or document library to which the alert applies. SP.Alert provides information about the alert,
    such as which alert template is used, the alert frequency, and the UserID of the user who created the alert.

    The AlertTime, ItemID, ListID and ListUrl properties are not included in the default scalar property
    set for this type.
    """

    @property
    def alert_frequency(self) -> Optional[int]:
        """Gets the time interval for sending the alert."""
        return self.properties.get("AlertFrequency", None)

    @property
    def alert_template_name(self) -> Optional[int]:
        """Gets the string representing the alert template name."""
        return self.properties.get("AlertTemplateName", None)

    @property
    def always_notify(self) -> Optional[bool]:
        """Gets a Boolean value that causes daily and weekly alerts to trigger, even if there is no matching event."""
        return self.properties.get("AlwaysNotify", None)

    @property
    def item(self) -> ListItem:
        """Gets the list item or document to which the alert applies."""
        from office365.sharepoint.listitems.listitem import ListItem

        return self.properties.get("Item", ListItem(self.context, ResourcePath("item", self.resource_path)))

    @property
    def user(self):
        """Gets user object that represents User for the alert."""
        from office365.sharepoint.principal.users.user import User

        return self.properties.get("User", User(self.context, ResourcePath("user", self.resource_path)))

    @property
    def list(self):
        """Gets list object that represents List for the alert."""
        from office365.sharepoint.lists.list import List

        return self.properties.get("List", List(self.context, ResourcePath("list", self.resource_path)))

    @property
    def alert_time(self) -> Optional[datetime]:
        """Gets the AlertTime property"""
        return self.properties.get("AlertTime", datetime.min)

    @property
    def alert_type(self) -> Optional[int]:
        """Gets the AlertType property"""
        return self.properties.get("AlertType", None)

    @property
    def delivery_channels(self) -> Optional[int]:
        """Gets the DeliveryChannels property"""
        return self.properties.get("DeliveryChannels", None)

    @property
    def event_type(self) -> Optional[int]:
        """Gets the EventType property"""
        return self.properties.get("EventType", None)

    @property
    def filter_(self) -> Optional[str]:
        """Gets the Filter property"""
        return self.properties.get("Filter", None)

    @property
    def id_(self) -> Optional[UUID]:
        """Gets the ID property"""
        return self.properties.get("ID", None)

    @property
    def item_id(self) -> Optional[int]:
        """Gets the ItemID property"""
        return self.properties.get("ItemID", None)

    @property
    def list_id(self) -> Optional[UUID]:
        """Gets the ListID property"""
        return self.properties.get("ListID", None)

    @property
    def list_url(self) -> Optional[str]:
        """Gets the ListUrl property"""
        return self.properties.get("ListUrl", None)

    @property
    def status(self) -> Optional[int]:
        """Gets the Status property"""
        return self.properties.get("Status", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    @property
    def user_id(self) -> Optional[int]:
        """Gets the UserId property"""
        return self.properties.get("UserId", None)

    @property
    def all_properties(self) -> PropertyValues:
        """Gets the AllProperties property"""
        return self.properties.get(
            "AllProperties", PropertyValues(self.context, ResourcePath("AllProperties", self.resource_path))
        )

    def update_alert(self) -> Self:
        """UpdateAlert operation."""
        qry = ServiceOperationQuery(self, "UpdateAlert", None, {}, None, None)
        self.context.add_query(qry)
        return self

    @property
    def filter(self) -> Optional[str]:
        """Gets the Filter property"""
        return self.properties.get("Filter", None)

    @property
    def id(self) -> Optional[UUID]:
        """Gets the ID property"""
        return self.properties.get("ID", None)
