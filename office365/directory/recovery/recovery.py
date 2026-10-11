from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.recovery.job_base import RecoveryJobBase
    from office365.directory.snapshot import Snapshot


class Recovery(Entity):
    @property
    def jobs(self) -> EntityCollection[RecoveryJobBase]:
        """Gets the jobs property"""
        from office365.directory.recovery.job_base import RecoveryJobBase

        return self.properties.get(
            "jobs",
            EntityCollection[RecoveryJobBase](self.context, RecoveryJobBase, ResourcePath("jobs", self.resource_path)),
        )

    @property
    def snapshots(self) -> EntityCollection[Snapshot]:
        """Gets the snapshots property"""
        from office365.directory.snapshot import Snapshot

        return self.properties.get(
            "snapshots",
            EntityCollection[Snapshot](self.context, Snapshot, ResourcePath("snapshots", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.entraRecoveryServices.Recovery"
