from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.recovery.resource_type_name import ResourceTypeName
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class RecoveryJobEntityNamesFilter(ClientValue):
    entityTypes: ClientValueCollection[ResourceTypeName] = field(
        default_factory=lambda: ClientValueCollection(ResourceTypeName)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.entraRecoveryServices.RecoveryJobEntityNamesFilter"
