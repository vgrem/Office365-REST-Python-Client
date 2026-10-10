from __future__ import annotations

from dataclasses import dataclass

from office365.intune.print.printers.incompatible_printer_settings import (
    IncompatiblePrinterSettings,
)
from office365.runtime.client_value import ClientValue


@dataclass
class AirPrintSettings(ClientValue):
    incompatiblePrinters: IncompatiblePrinterSettings = IncompatiblePrinterSettings.show

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AirPrintSettings"
