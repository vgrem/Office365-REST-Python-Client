from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.recovery.job import RecoveryJob
    from office365.directory.recovery.preview_job import RecoveryPreviewJob


class Snapshot(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def total_changed_objects(self) -> Optional[int]:
        """Gets the totalChangedObjects property"""
        return self.properties.get("totalChangedObjects", None)

    @property
    def recovery_jobs(self) -> EntityCollection[RecoveryJob]:
        """Gets the recoveryJobs property"""
        from office365.directory.recovery.job import RecoveryJob

        return self.properties.get(
            "recoveryJobs",
            EntityCollection[RecoveryJob](self.context, RecoveryJob, ResourcePath("recoveryJobs", self.resource_path)),
        )

    @property
    def recovery_preview_jobs(self) -> EntityCollection[RecoveryPreviewJob]:
        """Gets the recoveryPreviewJobs property"""
        from office365.directory.recovery.preview_job import RecoveryPreviewJob

        return self.properties.get(
            "recoveryPreviewJobs",
            EntityCollection[RecoveryPreviewJob](
                self.context, RecoveryPreviewJob, ResourcePath("recoveryPreviewJobs", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.entraRecoveryServices.Snapshot"
