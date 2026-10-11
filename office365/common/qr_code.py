from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.authentication.qr_code_image_details import (
        QrCodeImageDetails,
    )


class QrCode(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def expire_date_time(self) -> Optional[datetime]:
        """Gets the expireDateTime property"""
        return self.properties.get("expireDateTime", datetime.min)

    @property
    def image(self) -> QrCodeImageDetails:
        """Gets the image property"""
        from office365.directory.authentication.qr_code_image_details import (
            QrCodeImageDetails,
        )

        return self.properties.get("image", QrCodeImageDetails())

    @property
    def last_used_date_time(self) -> Optional[datetime]:
        """Gets the lastUsedDateTime property"""
        return self.properties.get("lastUsedDateTime", datetime.min)

    @property
    def start_date_time(self) -> Optional[datetime]:
        """Gets the startDateTime property"""
        return self.properties.get("startDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.QrCode"
