from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.outlook.calendar.email_address import EmailAddress
    from office365.outlook.mail.inferenceclassificationtype import (
        InferenceClassificationType,
    )


class InferenceClassificationOverride(Entity):
    @property
    def classify_as(self) -> InferenceClassificationType:
        """Gets the classifyAs property"""
        from office365.outlook.mail.inferenceclassificationtype import (
            InferenceClassificationType,
        )

        return self.properties.get("classifyAs", InferenceClassificationType.focused)

    @property
    def sender_email_address(self) -> EmailAddress:
        """Gets the senderEmailAddress property"""
        from office365.outlook.calendar.email_address import EmailAddress

        return self.properties.get("senderEmailAddress", EmailAddress())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.InferenceClassificationOverride"
