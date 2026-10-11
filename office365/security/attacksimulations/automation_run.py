from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.security.attacksimulations.simulationautomationrunstatus import (
        SimulationAutomationRunStatus,
    )


class SimulationAutomationRun(Entity):
    """Represents a run of an attack simulation automation on a tenant."""

    @property
    def simulation_id(self) -> Optional[str]:
        """"""
        return self.properties.get("simulationId", None)

    @property
    def end_date_time(self) -> Optional[datetime]:
        """Gets the endDateTime property"""
        return self.properties.get("endDateTime", datetime.min)

    @property
    def start_date_time(self) -> Optional[datetime]:
        """Gets the startDateTime property"""
        return self.properties.get("startDateTime", datetime.min)

    @property
    def status(self) -> SimulationAutomationRunStatus:
        """Gets the status property"""
        from office365.security.attacksimulations.simulationautomationrunstatus import (
            SimulationAutomationRunStatus,
        )

        return self.properties.get("status", SimulationAutomationRunStatus.unknown)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SimulationAutomationRun"
