from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue
from office365.security.alerts.registryhive import RegistryHive
from office365.security.alerts.registryoperation import RegistryOperation
from office365.security.alerts.registryvaluetype import RegistryValueType


@dataclass
class RegistryKeyState(ClientValue):
    hive: RegistryHive = RegistryHive.unknown
    key: str | None = None
    oldKey: str | None = None
    oldValueData: str | None = None
    oldValueName: str | None = None
    operation: RegistryOperation = RegistryOperation.unknown
    processId: int | None = None
    valueData: str | None = None
    valueName: str | None = None
    valueType: RegistryValueType = RegistryValueType.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RegistryKeyState"
