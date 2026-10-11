from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.certification_control import CertificationControl


@dataclass
class ComplianceInformation(ClientValue):
    certificationControls: ClientValueCollection[CertificationControl] = field(
        default_factory=lambda: ClientValueCollection(CertificationControl)
    )
    certificationName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ComplianceInformation"
