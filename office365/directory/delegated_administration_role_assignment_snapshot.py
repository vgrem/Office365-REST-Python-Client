from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.role_template import RoleTemplate
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class DelegatedAdministrationRoleAssignmentSnapshot(ClientValue):
    groupDisplayName: str | None = None
    groupId: str | None = None
    roleTemplates: ClientValueCollection[RoleTemplate] = field(
        default_factory=lambda: ClientValueCollection(RoleTemplate)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DelegatedAdministrationRoleAssignmentSnapshot"
