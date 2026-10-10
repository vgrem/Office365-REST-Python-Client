from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.directory.security.attacksimulations.targettedusertype import (
        TargettedUserType,
    )


@dataclass
class SimulationNotification(ClientValue):
    targettedUserType: TargettedUserType = TargettedUserType.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SimulationNotification"
