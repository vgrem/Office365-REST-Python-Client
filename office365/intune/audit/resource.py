from __future__ import annotations

from dataclasses import dataclass, field

from office365.intune.audit.property import AuditProperty
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class AuditResource(ClientValue):
    """A class containing the properties for Audit Resource.

    Args:
        audit_resource_type (str): Audit resource's type.
    """

    auditResourceType: str | None = None

    displayName: str | None = None

    modifiedProperties: ClientValueCollection[AuditProperty] = field(
        default_factory=lambda: ClientValueCollection(AuditProperty)
    )

    resourceId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AuditResource"
