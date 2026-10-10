from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


@dataclass
class AuditActor(ClientValue):
    """A class containing the properties for Audit Actor."""

    applicationDisplayName: str | None = None

    applicationId: str | None = None

    auditActorType: str | None = None

    ipAddress: str | None = None

    servicePrincipalName: str | None = None

    userId: str | None = None

    userPermissions: StringCollection = field(default_factory=StringCollection)

    userPrincipalName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AuditActor"
