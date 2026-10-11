from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.applications.applications_required_resource_access import (
    ApplicationsRequiredResourceAccess,
)
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class MultiTenantApplicationsToProvisionSnapshot(ClientValue):
    appId: str | None = None
    displayName: str | None = None
    objectId: str | None = None
    requiredResourceAccesses: ClientValueCollection[ApplicationsRequiredResourceAccess] = field(
        default_factory=lambda: ClientValueCollection(ApplicationsRequiredResourceAccess)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MultiTenantApplicationsToProvisionSnapshot"
