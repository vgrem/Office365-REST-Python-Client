from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.recovery.resource_type_name import ResourceTypeName
from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


@dataclass
class EntityTypeAndIds(ClientValue):
    entityIds: StringCollection = field(default_factory=StringCollection)
    entityType: ResourceTypeName = ResourceTypeName.user

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.entraRecoveryServices.EntityTypeAndIds"
