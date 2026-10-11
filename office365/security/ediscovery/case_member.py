from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.security.recipient_type import RecipientType


class EdiscoveryCaseMember(Entity):
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def smtp_address(self) -> Optional[str]:
        """Gets the smtpAddress property"""
        return self.properties.get("smtpAddress", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.EdiscoveryCaseMember"

    @property
    def recipient_type(self) -> RecipientType:
        """Gets the recipientType property"""
        from office365.security.recipient_type import RecipientType

        return self.properties.get("recipientType", RecipientType.user)
