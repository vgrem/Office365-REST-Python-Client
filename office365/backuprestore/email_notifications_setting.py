from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.backuprestore.notification_events_type import NotificationEventsType
    from office365.directory.rolemanagement.unifiedrole.notification_recipients import (
        NotificationRecipients,
    )


class EmailNotificationsSetting(Entity):
    @property
    def additional_events(self) -> NotificationEventsType:
        """Gets the additionalEvents property"""
        from office365.backuprestore.notification_events_type import (
            NotificationEventsType,
        )

        return self.properties.get("additionalEvents", NotificationEventsType.none)

    @property
    def is_enabled(self) -> Optional[bool]:
        """Gets the isEnabled property"""
        return self.properties.get("isEnabled", None)

    @property
    def recipients(self) -> NotificationRecipients:
        """Gets the recipients property"""
        from office365.directory.rolemanagement.unifiedrole.notification_recipients import (
            NotificationRecipients,
        )

        return self.properties.get("recipients", NotificationRecipients())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EmailNotificationsSetting"
