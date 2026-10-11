from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.identity_set import IdentitySet
    from office365.directory.protection.unitsbulkjobstatus import (
        ProtectionUnitsBulkJobStatus,
    )
    from office365.runtime.types.public_error import PublicError


class ProtectionUnitsBulkJobBase(Entity):
    @property
    def created_by(self) -> IdentitySet:
        """Gets the createdBy property"""
        from office365.directory.identity_set import IdentitySet

        return self.properties.get("createdBy", IdentitySet())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def error(self) -> PublicError:
        """Gets the error property"""
        from office365.runtime.types.public_error import PublicError

        return self.properties.get("error", PublicError())

    @property
    def last_modified_by(self) -> IdentitySet:
        """Gets the lastModifiedBy property"""
        from office365.directory.identity_set import IdentitySet

        return self.properties.get("lastModifiedBy", IdentitySet())

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def status(self) -> ProtectionUnitsBulkJobStatus:
        """Gets the status property"""
        from office365.directory.protection.unitsbulkjobstatus import (
            ProtectionUnitsBulkJobStatus,
        )

        return self.properties.get("status", ProtectionUnitsBulkJobStatus.unknown)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ProtectionUnitsBulkJobBase"
