from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class WindowsInformationProtectionApp(ClientValue):
    denied: bool | None = None
    description: str | None = None
    displayName: str | None = None
    productName: str | None = None
    publisherName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsInformationProtectionApp"
