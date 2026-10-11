from __future__ import annotations

from typing import Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection


class UnifiedRoleManagementPolicyNotificationRule(Entity):
    @property
    def is_default_recipients_enabled(self) -> Optional[bool]:
        """Gets the isDefaultRecipientsEnabled property"""
        return self.properties.get("isDefaultRecipientsEnabled", None)

    @property
    def notification_level(self) -> Optional[str]:
        """Gets the notificationLevel property"""
        return self.properties.get("notificationLevel", None)

    @property
    def notification_recipients(self) -> StringCollection:
        """Gets the notificationRecipients property"""
        return self.properties.get("notificationRecipients", StringCollection())

    @property
    def notification_type(self) -> Optional[str]:
        """Gets the notificationType property"""
        return self.properties.get("notificationType", None)

    @property
    def recipient_type(self) -> Optional[str]:
        """Gets the recipientType property"""
        return self.properties.get("recipientType", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleManagementPolicyNotificationRule"
