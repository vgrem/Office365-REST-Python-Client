from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class RegistryValueEvidence(ClientValue):
    mdeDeviceId: str | None = None
    registryHive: str | None = None
    registryKey: str | None = None
    registryValue: str | None = None
    registryValueName: str | None = None
    registryValueType: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.RegistryValueEvidence"
