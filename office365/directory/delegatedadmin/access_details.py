from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.unified_role import UnifiedRole
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class DelegatedAdminAccessDetails(ClientValue):
    unifiedRoles: ClientValueCollection[UnifiedRole] = field(default_factory=lambda: ClientValueCollection(UnifiedRole))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DelegatedAdminAccessDetails"
