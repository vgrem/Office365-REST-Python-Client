from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class SecurityVendorInformation(ClientValue):
    provider: str | None = None
    providerVersion: str | None = None
    subProvider: str | None = None
    vendor: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SecurityVendorInformation"
