from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.backuprestore.artifactrestorestatus import ArtifactRestoreStatus
    from office365.backuprestore.destinationtype import DestinationType
    from office365.common.restore_point import RestorePoint
    from office365.runtime.types.public_error import PublicError


class RestoreArtifactBase(Entity):
    @property
    def completion_date_time(self) -> Optional[datetime]:
        """Gets the completionDateTime property"""
        return self.properties.get("completionDateTime", datetime.min)

    @property
    def destination_type(self) -> DestinationType:
        """Gets the destinationType property"""
        from office365.backuprestore.destinationtype import DestinationType

        return self.properties.get("destinationType", DestinationType.new)

    @property
    def error(self) -> PublicError:
        """Gets the error property"""
        from office365.runtime.types.public_error import PublicError

        return self.properties.get("error", PublicError())

    @property
    def start_date_time(self) -> Optional[datetime]:
        """Gets the startDateTime property"""
        return self.properties.get("startDateTime", datetime.min)

    @property
    def status(self) -> ArtifactRestoreStatus:
        """Gets the status property"""
        from office365.backuprestore.artifactrestorestatus import ArtifactRestoreStatus

        return self.properties.get("status", ArtifactRestoreStatus.added)

    @property
    def restore_point(self) -> RestorePoint:
        """Gets the restorePoint property"""
        from office365.common.restore_point import RestorePoint

        return self.properties.get(
            "restorePoint", RestorePoint(self.context, ResourcePath("restorePoint", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RestoreArtifactBase"
