from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.outlook.mail.item_body import ItemBody
from office365.runtime.client_value import ClientValue


@dataclass
class PresenceStatusMessage(ClientValue):
    """Represents a presence status message related to the presence of a user in Microsoft Teams.

    Fields:
        expiryDateTime: Time in which the status message expires. If not provided, the status
            message does not expire.
        message: Status message item.
        publishedDateTime: Time in which the status message was published.
    """

    expiryDateTime: DateTimeTimeZone = field(default_factory=DateTimeTimeZone)
    message: ItemBody = field(default_factory=ItemBody)
    publishedDateTime: datetime | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PresenceStatusMessage"
