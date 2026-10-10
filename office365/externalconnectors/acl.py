from __future__ import annotations

from dataclasses import dataclass

from office365.directory.identitygovernance.entitlementmanagement.accesspackage.accesstype import (
    AccessType,
)
from office365.externalconnectors.acl_type import AclType
from office365.runtime.client_value import ClientValue


@dataclass
class Acl(ClientValue):
    accessType: AccessType = AccessType.grant
    value: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.externalConnectors.Acl"

    type: AclType = AclType.user
