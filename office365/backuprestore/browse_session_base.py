from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.backuprestore.restoresessions.browse_session_status import (
        BrowseSessionStatus,
    )
    from office365.runtime.types.public_error import PublicError


class BrowseSessionBase(Entity):
    @property
    def backup_size_in_bytes(self) -> Optional[str]:
        """Gets the backupSizeInBytes property"""
        return self.properties.get("backupSizeInBytes", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def error(self) -> PublicError:
        """Gets the error property"""
        from office365.runtime.types.public_error import PublicError

        return self.properties.get("error", PublicError())

    @property
    def expiration_date_time(self) -> Optional[datetime]:
        """Gets the expirationDateTime property"""
        return self.properties.get("expirationDateTime", datetime.min)

    @property
    def restore_point_date_time(self) -> Optional[datetime]:
        """Gets the restorePointDateTime property"""
        return self.properties.get("restorePointDateTime", datetime.min)

    @property
    def restore_point_id(self) -> Optional[str]:
        """Gets the restorePointId property"""
        return self.properties.get("restorePointId", None)

    @property
    def status(self) -> BrowseSessionStatus:
        """Gets the status property"""
        from office365.backuprestore.restoresessions.browse_session_status import (
            BrowseSessionStatus,
        )

        return self.properties.get("status", BrowseSessionStatus.creating)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BrowseSessionBase"
