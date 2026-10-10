from __future__ import annotations

from dataclasses import dataclass, field

from office365.outlook.mail.physical_address import PhysicalAddress
from office365.runtime.client_value import ClientValue


@dataclass
class WhoisContact(ClientValue):
    address: PhysicalAddress = field(default_factory=PhysicalAddress)
    email: str | None = None
    fax: str | None = None
    name: str | None = None
    organization: str | None = None
    telephone: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.WhoisContact"
