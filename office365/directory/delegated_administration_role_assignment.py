from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from office365.directory.role_template import RoleTemplate
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.directory.groups.group import Group


@dataclass
class DelegatedAdministrationRoleAssignment(ClientValue):
    groupDisplayName: str | None = None
    roleTemplates: ClientValueCollection[RoleTemplate] = field(
        default_factory=lambda: ClientValueCollection(RoleTemplate)
    )
    group: Group | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DelegatedAdministrationRoleAssignment"
