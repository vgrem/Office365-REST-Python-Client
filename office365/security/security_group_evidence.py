from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from office365.runtime.client_value import ClientValue


@dataclass
class SecurityGroupEvidence(ClientValue):
    activeDirectoryObjectGuid: UUID | None = None
    displayName: str | None = None
    distinguishedName: str | None = None
    friendlyName: str | None = None
    securityGroupId: str | None = None
    sid: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.SecurityGroupEvidence"
