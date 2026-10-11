from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.administration.telephone_number_long_running_operation import (
    TelephoneNumberLongRunningOperation,
)

if TYPE_CHECKING:
    from office365.teams.administration.number_assignment import NumberAssignment


class TelephoneNumberManagementRoot(Entity):
    @property
    def operations(self) -> EntityCollection[TelephoneNumberLongRunningOperation]:
        """Gets the operations property"""
        return self.properties.get(
            "operations",
            EntityCollection[TelephoneNumberLongRunningOperation](
                self.context, TelephoneNumberLongRunningOperation, ResourcePath("operations", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.teamsAdministration.TelephoneNumberManagementRoot"

    @property
    def number_assignments(self) -> EntityCollection[NumberAssignment]:
        """Gets the numberAssignments property"""
        from office365.teams.administration.number_assignment import NumberAssignment

        return self.properties.get(
            "numberAssignments",
            EntityCollection[NumberAssignment](
                self.context, NumberAssignment, ResourcePath("numberAssignments", self.resource_path)
            ),
        )
