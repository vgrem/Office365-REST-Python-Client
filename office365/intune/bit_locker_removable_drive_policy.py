from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.configurations.windows.bitlockerencryptionmethod import (
    BitLockerEncryptionMethod,
)
from office365.runtime.client_value import ClientValue


@dataclass
class BitLockerRemovableDrivePolicy(ClientValue):
    blockCrossOrganizationWriteAccess: bool | None = None
    encryptionMethod: BitLockerEncryptionMethod = BitLockerEncryptionMethod.aesCbc128
    requireEncryptionForWriteAccess: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BitLockerRemovableDrivePolicy"
