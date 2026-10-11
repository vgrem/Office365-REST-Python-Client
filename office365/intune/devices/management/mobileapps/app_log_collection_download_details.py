from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.management.applogdecryptionalgorithm import (
    AppLogDecryptionAlgorithm,
)
from office365.runtime.client_value import ClientValue


@dataclass
class AppLogCollectionDownloadDetails(ClientValue):
    appLogDecryptionAlgorithm: AppLogDecryptionAlgorithm = AppLogDecryptionAlgorithm.aes256
    decryptionKey: str | None = None
    downloadUrl: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AppLogCollectionDownloadDetails"
