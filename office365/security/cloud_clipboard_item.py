from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.security.cloud_clipboard_item_payload import (
        CloudClipboardItemPayload,
    )


class CloudClipboardItem(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def expiration_date_time(self) -> Optional[datetime]:
        """Gets the expirationDateTime property"""
        return self.properties.get("expirationDateTime", datetime.min)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def payloads(self) -> ClientValueCollection[CloudClipboardItemPayload]:
        """Gets the payloads property"""
        from office365.security.cloud_clipboard_item_payload import (
            CloudClipboardItemPayload,
        )

        return self.properties.get(
            "payloads", ClientValueCollection[CloudClipboardItemPayload](CloudClipboardItemPayload)
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CloudClipboardItem"
