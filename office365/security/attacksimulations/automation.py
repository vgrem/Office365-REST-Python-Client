from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.permissions.email_identity import EmailIdentity
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.security.attacksimulations.automation_run import (
    SimulationAutomationRun,
)

if TYPE_CHECKING:
    from office365.security.attacksimulations.simulationautomationstatus import (
        SimulationAutomationStatus,
    )


class SimulationAutomation(Entity):
    """Represents simulation automation created to run on a tenant."""

    @odata(name="createdBy")
    @property
    def created_by(self) -> EmailIdentity:
        """Identity of the user who created the attack simulation automation."""
        return self.properties.get("createdBy", EmailIdentity())

    @property
    def runs(self) -> EntityCollection[SimulationAutomationRun]:
        """A collection of simulation automation runs."""
        return self.properties.get(
            "runs",
            EntityCollection(
                self.context,
                SimulationAutomationRun,
                ResourcePath("runs", self.resource_path),
            ),
        )

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def last_modified_by(self) -> EmailIdentity:
        """Gets the lastModifiedBy property"""
        from office365.directory.permissions.email_identity import EmailIdentity

        return self.properties.get("lastModifiedBy", EmailIdentity())

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def last_run_date_time(self) -> Optional[datetime]:
        """Gets the lastRunDateTime property"""
        return self.properties.get("lastRunDateTime", datetime.min)

    @property
    def next_run_date_time(self) -> Optional[datetime]:
        """Gets the nextRunDateTime property"""
        return self.properties.get("nextRunDateTime", datetime.min)

    @property
    def status(self) -> SimulationAutomationStatus:
        """Gets the status property"""
        from office365.security.attacksimulations.simulationautomationstatus import (
            SimulationAutomationStatus,
        )

        return self.properties.get("status", SimulationAutomationStatus.unknown)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SimulationAutomation"
