from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.backuprestore.destinationtype import DestinationType
    from office365.backuprestore.restoreartifactsbulkrequeststatus import (
        RestoreArtifactsBulkRequestStatus,
    )
    from office365.backuprestore.restorepoints.preference import RestorePointPreference
    from office365.backuprestore.restorepoints.tags import RestorePointTags
    from office365.backuprestore.time_period import TimePeriod
    from office365.directory.identity_set import IdentitySet
    from office365.runtime.types.public_error import PublicError


class RestoreArtifactsBulkRequestBase(Entity):
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
    def destination_type(self) -> DestinationType:
        """Gets the destinationType property"""
        from office365.backuprestore.destinationtype import DestinationType

        return self.properties.get("destinationType", DestinationType.new)

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
    def protection_time_period(self) -> TimePeriod:
        """Gets the protectionTimePeriod property"""
        from office365.backuprestore.time_period import TimePeriod

        return self.properties.get("protectionTimePeriod", TimePeriod())

    @property
    def protection_unit_ids(self) -> StringCollection:
        """Gets the protectionUnitIds property"""
        return self.properties.get("protectionUnitIds", StringCollection())

    @property
    def restore_point_preference(self) -> RestorePointPreference:
        """Gets the restorePointPreference property"""
        from office365.backuprestore.restorepoints.preference import (
            RestorePointPreference,
        )

        return self.properties.get("restorePointPreference", RestorePointPreference.latest)

    @property
    def status(self) -> RestoreArtifactsBulkRequestStatus:
        """Gets the status property"""
        from office365.backuprestore.restoreartifactsbulkrequeststatus import (
            RestoreArtifactsBulkRequestStatus,
        )

        return self.properties.get("status", RestoreArtifactsBulkRequestStatus.unknown)

    @property
    def tags(self) -> RestorePointTags:
        """Gets the tags property"""
        from office365.backuprestore.restorepoints.tags import RestorePointTags

        return self.properties.get("tags", RestorePointTags.none)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RestoreArtifactsBulkRequestBase"
