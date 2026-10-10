from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.application_resource_permission import (
    ApplicationResourcePermission,
)
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class ApplicationsRequiredResourceAccess(ClientValue):
    permissions: ClientValueCollection[ApplicationResourcePermission] = field(
        default_factory=lambda: ClientValueCollection(ApplicationResourcePermission)
    )
    resourceAppId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ApplicationsRequiredResourceAccess"
