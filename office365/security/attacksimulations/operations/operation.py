from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.onedrive.operations.long_running import LongRunningOperation

if TYPE_CHECKING:
    from office365.security.attacksimulations.operations.type import (
        AttackSimulationOperationType,
    )


class AttackSimulationOperation(LongRunningOperation):
    """Represents the status of a long-running attack simulation training operation."""

    @property
    def percentage_completed(self) -> Optional[int]:
        """Gets the percentageCompleted property"""
        return self.properties.get("percentageCompleted", None)

    @property
    def tenant_id(self) -> Optional[str]:
        """Gets the tenantId property"""
        return self.properties.get("tenantId", None)

    @property
    def type(self) -> AttackSimulationOperationType:
        """Gets the type property"""
        from office365.security.attacksimulations.operations.type import (
            AttackSimulationOperationType,
        )

        return self.properties.get("type", AttackSimulationOperationType.createSimualation)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttackSimulationOperation"
