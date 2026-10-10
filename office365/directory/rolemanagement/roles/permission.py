from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.rolemanagement.resource_action import ResourceAction
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class RolePermission(ClientValue):
    """Contains the set of ResourceActions determining the allowed and not allowed permissions for each role."""

    resourceActions: ClientValueCollection[ResourceAction] = field(
        default_factory=lambda: ClientValueCollection(ResourceAction)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RolePermission"
