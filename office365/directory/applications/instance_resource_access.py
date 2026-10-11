from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.applications.resource_permission import ResourcePermission
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class InstanceResourceAccess(ClientValue):
    permissions: ClientValueCollection[ResourcePermission] = field(
        default_factory=lambda: ClientValueCollection(ResourcePermission)
    )
    resourceAppId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.InstanceResourceAccess"
