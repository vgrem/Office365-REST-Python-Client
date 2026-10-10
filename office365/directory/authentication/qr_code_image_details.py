from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.directory.authentication.error_correction_level import (
        ErrorCorrectionLevel,
    )


@dataclass
class QrCodeImageDetails(ClientValue):
    binaryValue: bytes | None = None
    rawContent: bytes | None = None
    version: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.QrCodeImageDetails"

    errorCorrectionLevel: ErrorCorrectionLevel = ErrorCorrectionLevel.m
