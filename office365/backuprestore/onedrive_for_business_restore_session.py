from __future__ import annotations

from typing import TYPE_CHECKING

from office365.common.restore_session_base import RestoreSessionBase
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.drive_restore_artifact import DriveRestoreArtifact
    from office365.common.drive_restore_artifacts_bulk_addition_request import (
        DriveRestoreArtifactsBulkAdditionRequest,
    )
    from office365.common.granular_drive_restore_artifact import (
        GranularDriveRestoreArtifact,
    )


class OneDriveForBusinessRestoreSession(RestoreSessionBase):
    @property
    def drive_restore_artifacts(self) -> EntityCollection[DriveRestoreArtifact]:
        """Gets the driveRestoreArtifacts property"""
        from office365.common.drive_restore_artifact import DriveRestoreArtifact

        return self.properties.get(
            "driveRestoreArtifacts",
            EntityCollection[DriveRestoreArtifact](
                self.context, DriveRestoreArtifact, ResourcePath("driveRestoreArtifacts", self.resource_path)
            ),
        )

    @property
    def drive_restore_artifacts_bulk_addition_requests(
        self,
    ) -> EntityCollection[DriveRestoreArtifactsBulkAdditionRequest]:
        """Gets the driveRestoreArtifactsBulkAdditionRequests property"""
        from office365.common.drive_restore_artifacts_bulk_addition_request import (
            DriveRestoreArtifactsBulkAdditionRequest,
        )

        return self.properties.get(
            "driveRestoreArtifactsBulkAdditionRequests",
            EntityCollection[DriveRestoreArtifactsBulkAdditionRequest](
                self.context,
                DriveRestoreArtifactsBulkAdditionRequest,
                ResourcePath("driveRestoreArtifactsBulkAdditionRequests", self.resource_path),
            ),
        )

    @property
    def granular_drive_restore_artifacts(self) -> EntityCollection[GranularDriveRestoreArtifact]:
        """Gets the granularDriveRestoreArtifacts property"""
        from office365.common.granular_drive_restore_artifact import (
            GranularDriveRestoreArtifact,
        )

        return self.properties.get(
            "granularDriveRestoreArtifacts",
            EntityCollection[GranularDriveRestoreArtifact](
                self.context,
                GranularDriveRestoreArtifact,
                ResourcePath("granularDriveRestoreArtifacts", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OneDriveForBusinessRestoreSession"
