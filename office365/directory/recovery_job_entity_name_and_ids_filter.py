from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.entity_type_and_ids import EntityTypeAndIds
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class RecoveryJobEntityNameAndIdsFilter(ClientValue):
    filterValues: ClientValueCollection[EntityTypeAndIds] = field(
        default_factory=lambda: ClientValueCollection(EntityTypeAndIds)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.entraRecoveryServices.RecoveryJobEntityNameAndIdsFilter"
