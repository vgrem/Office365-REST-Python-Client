from __future__ import annotations

from dataclasses import dataclass

from office365.directory.security.attacksimulations.targettedusertype import (
    TargettedUserType,
)
from office365.runtime.client_value import ClientValue


@dataclass
class SimulationNotification(ClientValue):
    targettedUserType: TargettedUserType = TargettedUserType.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SimulationNotification"
