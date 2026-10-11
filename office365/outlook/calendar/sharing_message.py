from __future__ import annotations

from typing import Optional

from office365.outlook.calendar.sharing.message_action import (
    CalendarSharingMessageAction,
)
from office365.outlook.mail.messages.message import Message
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.odata_property import odata


class CalendarSharingMessage(Message):
    """"""

    @odata(name="sharingMessageAction")
    @property
    def sharing_message_action(self) -> CalendarSharingMessageAction:
        """"""
        return self.properties.setdefault("sharingMessageAction", CalendarSharingMessageAction())

    @property
    def can_accept(self) -> Optional[bool]:
        """Gets the canAccept property"""
        return self.properties.get("canAccept", None)

    @property
    def sharing_message_actions(self) -> ClientValueCollection[CalendarSharingMessageAction]:
        """Gets the sharingMessageActions property"""
        from office365.outlook.calendar.sharing.message_action import (
            CalendarSharingMessageAction,
        )

        return self.properties.get(
            "sharingMessageActions", ClientValueCollection[CalendarSharingMessageAction](CalendarSharingMessageAction)
        )

    @property
    def suggested_calendar_name(self) -> Optional[str]:
        """Gets the suggestedCalendarName property"""
        return self.properties.get("suggestedCalendarName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CalendarSharingMessage"
