from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class QrCodeImageDetails(ClientValue):
    binaryValue: bytes | None = None
    rawContent: bytes | None = None
    version: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.QrCodeImageDetails"
